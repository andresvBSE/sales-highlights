# :earth_americas: GDP dashboard template

A simple Streamlit app that includes ChatGPT generated textual highlights for a demo dashboard of sales accross diferent stores.

[![Test the this demo on ](https://highlightssalesdashboard.streamlit.app)

## How It works?

Through ChatGPT API it generates concise textual highlights from summary tables. It automatically processes tables containing sales data and outputs significant changes, helping users quickly grasp key insights from the data.

## Example:

Given a table like the next:

| Store | Previous Week | Current Week | Weekly Variation | Weekly Variation % |
|-------|---------------|--------------|------------------|--------------------|
| Total | 6,665,548.38  | 6,342,993.81 | -322,555.0       | -4.84%             |
| 4     | 2,209,835.43  | 2,133,026.07 | -76,809.0        | -3.48%             |
| 2     | 1,998,321.04  | 1,900,745.13 | -97,576.0        | -4.88%             |
| 1     | 1,670,785.97  | 1,573,072.81 | -97,713.0        | -5.85%             |
| 3     | 443,557.65    | 410,804.39   | -32,753.0        | -7.38%             |
| 5     | 343,048.29    | 325,345.41   | -17,703.0        | -5.16%             |

The script is able to get highlights like: "Total sales decreased by $322,555.0 (4.84%). The decrease was driven mainly by a reduction of $97,713.0 (5.85%) in store 1."

## Data
Walmart Sales data taken from  [![kaggle ](https://www.kaggle.com/datasets/mikhail1681/walmart-sales)


## Prerequisites
Before you begin, you will need:
- Python 3.8 or higher
- API key for OpenAI ChatGPT
- Install libraries from requirements.txt