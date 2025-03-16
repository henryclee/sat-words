
# SAT WORDS

I was looking to make a study guide for SAT vocabulary words, and found this list of words, conveniently separated into high/medium/low frequency words:

https://sites.google.com/site/sesamewords/home?authuser=0

However, I find that studying vocabulary words in the format word / synonym / definition is really tedious. I believe that the easiest way to learn new words is by reading them in context.

I made a basic tool that queries Gemini's free API to generate 2 sentences for each word in the list. I specifically prompted the API to generate sentences that are not only memorable, but also use the word in the sentence such that the meaning is clear from the context of the sentence.

The code is a little sloppy, since this was meant to be a one-time use tool, but hopefully other people might find this to be a useful resource.

The text files with the output are:

./study_guide/hi_freq_words_sg.txt

./study_guide/med_freq_words_sg.txt

./study_guide/low_freq_words_sg.txt
