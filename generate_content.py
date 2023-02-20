import openai
import sys

openai.api_key = "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"
prompt = "viết bài miêu tả núi cấm và đặc sản núi cấm"
results = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt + "",
    temperature=0.5,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stream=True
)
for line in results:

    print(line.choices[0].text)

# for resp in openai.Completion.create(model='code-davinci-002', prompt='viết bài miêu tả núi cấm và đặc sản núi cấm', max_tokens=512, stream=True):
#     sys.stdout.write(resp.choices[0].text)
#     sys.stdout.flush()