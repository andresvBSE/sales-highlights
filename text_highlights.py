import pandas as pd

import numpy as np

from openai import OpenAI
from transformers import GPT2Tokenizer

import a_env_vars
import os
os.environ["OPENAI_API_KEY"] = a_env_vars.api_key

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Get initial data
df = pd.read_csv("Walmart_Sales.csv")
df = df.query("Store<6") # only 5 stores
df["Date"] = pd.to_datetime(df['Date'], format="%d-%m-%Y")
df["Date S F"] = df['Date'].dt.strftime("%Y-%m-%d")
df.sort_values(by="Date", inplace=True) # Sort by date ascending


### Class helpers

class CreateTable:
    def __init__(self, df, current_week, last_week):
        self.df = df.sort_values(by="Date")
        self.current_week = current_week
        self.last_week = last_week

    def create_summary_table(self):
        self.result_df = self.df[self.df["Date"].isin([self.current_week, self.last_week])]
        
        # Pivot table
        self.result_df = self.result_df.pivot_table(index='Store', columns="Date", values=["Weekly_Sales"])
        self.result_df.columns = ["Previous Week", "Current Week"]
        self.result_df.reset_index(inplace=True)

        # Total row
        total_row = pd.DataFrame([{
                        "Store" : "Total",
                        "Previous Week":  self.result_df["Previous Week"].sum(),
                        "Current Week":  self.result_df["Current Week"].sum()
                         }]
                    )

        self.result_df = pd.concat([self.result_df, total_row])

        # Variation columns
        self.result_df["Weekly Variation"] = np.round(self.result_df["Current Week"] - self.result_df["Previous Week"], 0)
        self.result_df["Weekly Variation %"] = np.round((self.result_df["Weekly Variation"] / self.result_df["Previous Week"]) * 100, 2)
        self.result_df["Change Type"] = np.where(self.result_df["Weekly Variation"]>0, "increase", "decrease")


        self.result_df = self.result_df.sort_values(by="Current Week",ascending=False).reset_index(drop=True)

        return self.result_df
    
    def create_summary_text(self):
        summary_list = []

        for idx in self.result_df.index:
            if idx == 0:
                text = "Total Sales changed in {} dolars wich represents a {} of {} percent. \n".format(self.result_df.at[idx, "Weekly Variation"], self.result_df.at[idx, "Change Type"], self.result_df.at[idx, "Weekly Variation %"])
                #print(text)
            else:
                text = "Sales in store {} changed {} dolars wich represents a {} of {} percent.\n".format(self.result_df.at[idx, "Store"], self.result_df.at[idx, "Weekly Variation"], self.result_df.at[idx, "Change Type"], self.result_df.at[idx, "Weekly Variation %"])
                #print(text)

            summary_list.append(text)
            summary_text = ''.join(summary_list)

        return summary_text


class CreateHighlights:
    def __init__(self, text, model="gpt-4o-mini") -> None:
        self.text = text
        self.model = model
        self.prompt = f"""
            You will be provided with text delimited by triple quotes about sales in a retail store chain. You must
            write a text with the next format:

            - Total sales increased by (value $) (value %). The increase was driven mainly by an expansion of (value $) (value %) in the store X.

            when total sales decreased, change the sense of the sentence:

            \"\"\"{self.text}\"\"\"
        """

    def count_tokens(self, text_to_ctokens):
        self.text_to_ctokens = text_to_ctokens
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        tokens = tokenizer.encode(self.text_to_ctokens)
        return len(tokens)


    def get_highlights(self):
        # Message to return
        messages = [{"role": "user", "content": self.prompt}]
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        self.returned_message = response.choices[0].message.content
        return self.returned_message
    
    def used_tokes(self):
        self.prompt_tokens = self.count_tokens(self.prompt)
        self.returned_tokens =  self.count_tokens(self.returned_message)
        self.total_tokens =  self.prompt_tokens + self.returned_tokens
        #print("Prompt tokens:", self.count_tokens(self.prompt), "Message tokens:", self.count_tokens(self.returned_message), "Total:", self.total_tokens)
        return self.total_tokens
    
    def total_cost(self):
        """
        Given the cost:
        - Input: 0,50 US$ / 1M tokens
        - Output: 1,50 US$ / 1M tokens
        """
        self.input_cost = self.prompt_tokens * 0.5 / 1000000 # prompt cost
        self.output_cost = self.returned_tokens * 1.5 / 1000000 # prompt cost
        self.total_cost = self.input_cost + self.output_cost
        return self.total_cost
    


# Data frame with highlights
# Get the pairs of weeks (current, previous)
weeks_lists = [i for i in df["Date S F"].unique()]
week_tuples = [(weeks_lists[i], weeks_lists[i-1]) for i in range(1,len(weeks_lists))]
print(len(week_tuples))


# Run a save results
highlights_list = [] 

for week_pair in week_tuples:
    current_week = week_pair[0]
    previous_week = week_pair[1]

    summary = CreateTable(df, current_week, previous_week)
    summ_table = summary.create_summary_table()
    summ_text = summary.create_summary_text()

    highl_t = CreateHighlights(summ_text)
    high_text = highl_t.get_highlights()

    highlights_list.append({
        "Week" : current_week,
        "Highlights" : high_text,
    })

df_hihglights = pd.DataFrame(highlights_list)
df_out = pd.merge(df, df_hihglights, left_on="Date S F", right_on="Week", how="left")
df_out.to_csv("data/highlights.csv") # Export