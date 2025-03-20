
# SAT WORDS

I was looking to make a study guide for SAT vocabulary words, and found this list of words, conveniently separated into high/medium/low frequency words:

https://sites.google.com/site/sesamewords/home?authuser=0

However, I find that studying vocabulary words in the format word / synonym / definition is really tedious. I believe that the easiest way to learn new words is by reading them in context.

I made a basic tool that queries Gemini's free API to generate 2 sentences for each word in the list. I specifically prompted the API to generate sentences that are not only memorable, but also use the word in the sentence such that the meaning is clear from the context of the sentence.

The text files with the output are:

./sat_words_tools/study_guide/hi_freq_words_sg.txt

./sat_words_tools/study_guide/med_freq_words_sg.txt

./sat_words_tools/study_guide/low_freq_words_sg.txt

I'm also working on making this into a fullstack project, so it can be accessed via a locally hosted website