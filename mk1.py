
# get youtube link
# get transcript from link
# pass transcript and prompt to ai
# output the timestamps

import re
import requests
from yt_dlp import YoutubeDL

def fetch_transcript(video):

    with YoutubeDL({'skip_download':True, 'quiet':True}) as ydl:
        info = ydl.extract_info(video, download=False)
        # now we have the video's meta data stored in 'info' dictionary

    captions = info.get('automatic_captions',{}).get('en',[])
    # now we have the link to each engilsh transcript format

    for fmt in captions:
        # going through all the formats
        if 'json3' in fmt.get('url', ''):
            # looking for json 3 format, which has the relevant video info
            # checking url key (because ext isn't always there)
            # if the url value has the string 'json3' in it, it's correct
            response = requests.get(fmt['url'])
            # get the transcript from the link
            #(info, captions, fmt are all dicts)
            data = response.json()
            # convert the info json into a dictionary

            transcript = []
            for event in data.get('events', []):
                # event is a key in a dict that has our relevant info
                # it is a list of dictionaries
                start = event.get('tStartMs')
                # Start time in milliseconds
                segs = event.get('segs')
                # seg is a key in event
                # it is a list of dicts, each containing a word

                if start and segs:
                    # this is needed cause some segs dont' exist
                    text = "".join(seg.get('utf8', '') for seg in segs).strip()
                    # take the word and keep appending it, to make a sentence

                    if text: # this is needed since some text is just a blank
                        m, s = divmod(start // 1000, 60)
                        # getting minutes and seconds
                        timestamp = f"{int(m)}:{int(s):02d}"
                        # turning to string, formatting it
                        transcript.append(f"{timestamp} {text}")
                        # now we have created one line in the timestamps

    ##j = 0
    #for i in (transcript):
    #    #j+=1
    #    if (len(i) > 12): #and j%5 == 1:
    #        print(i[:40]+"...")
    
    return transcript, info.get("duration") # need the duration for dynamic chunking
                
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

UNWANTED_PHRASES = ["[Music]", "[Applause]", "[Laughter]", "[Noise]"]

def generate_timestamps(transcript, video_duration):
    name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSeq2SeqLM.from_pretrained(name)

    # dynamically adjust chunking frequency
    #target_num_chunks = max(5, min(10, int(video_duration // 360)))  # 5 for 20min, 10 for 60min+
    #lines_per_chunk = max(5, len(transcript) // target_num_chunks)
    # the above 2 lines of code are really useless, they just give worse outputs
    
    prompts = []
    timestamps = []
    results = []
    this_chunk = ""
    j = 1
    
    for i in transcript:
        this_chunk += " " + i.split(' ', 1)[1] if ' ' in i else i

        # preprocessing (removing unnecessary tokens)
        line = i
        for phrase in UNWANTED_PHRASES:
            line = line.replace(phrase, "")
        line = re.sub(r"[!?.,]{2,}", ".", line)  # collapse multiple punctuations
        line = re.sub(r"[^\x00-\x7F]+", "", line)  # remove non-ASCII
        line = line.strip()
        if not line:
            continue
        
        if not i.strip(): continue
        
        j+=1
        if j%30 == 1:
            start = i.split(' ', 1)[0]
            prompt = (
                "Generate a short and engaging Youtube chapter title (2-6 words) "
                f"for the following video transcript chunk:\n\n{this_chunk}"
            )
            prompts.append(prompt)
            timestamps.append(start)
            this_chunk = ""

    # batching logic
    BATCH_SIZE=4
    for i in range(0, len(prompts), BATCH_SIZE):
        batch_prompts = prompts[i:i + BATCH_SIZE]
        batch_timestamps = timestamps[i:i+BATCH_SIZE]
        
        inputs = tokenizer(batch_prompts, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model.generate(**inputs, max_new_tokens=20)

        # postprocessing (removing spaces, making first letter capital)
        titles = [tokenizer.decode(o, skip_special_tokens=True).strip().title() for o in outputs]
        
        batch_results = [f"{ts} {title}" for ts, title in zip(batch_timestamps, titles)]
        results.extend(batch_results)

    for r in results:
        print(r)

if __name__ == "__main__":
    #video = "https://www.youtube.com/watch?v=CmrjSe01LMA"
    video = str(input("Paste youtube video link: "))
    #print(video)
    transcript, video_duration = fetch_transcript(video)
    #transcript = ['0:01 when she arrived she seemed quite scared', '0:04 and she wanted her mom', '0:07 Eddie Pico was circling the window', "0:10 what's a part of their natural behavior", "0:12 they'll suckle on their moms to get the", '0:14 milk', '0:17 it was a sign that she missed her mother', '0:18 and she was looking for her', '0:21 [Music]', '0:27 we got a call from somebody that worked', '0:30 at a Aquaculture farm', '0:35 is stuck on top of an oyster Trestle bed', '0:39 she was surrounded by heavy machinery', '0:41 probably scared away the mother', '0:45 [Music]', '0:49 we gave her a wetsuit mom which', '0:51 basically is recycled wetsuit all kind', '0:54 of packed together kind of resembles the', '0:56 mother seal', '0:57 she cuddled up to it she was fast asleep', '1:00 cuddled into the wetsuit Mall', '1:03 the ultimate goal was to get her healthy', '1:06 and to get her up to weight so that she', '1:09 could be released back into the wild and', '1:10 flourish as a wild seal', '1:14 [Music]', '1:17 we started fish', '1:19 surprised us all and it was one of the', '1:21 first comments used to start eating', '1:23 despite being the smallest', '1:24 [Music]', "1:27 but I don't want to leave at the start", '1:29 she was quiet but once that kind of', '1:31 settled down she let us know that she', '1:33 was feistier everybody had to be careful', '1:37 of elipica', '1:40 any Pico would know when you were coming', '1:42 to teen she loved her bathtub and she', "1:44 didn't like anyone else near the bathtub", '1:47 when I was trying to clean her bathtub', '1:49 she was slapping the brush', '1:51 and then she was back', '1:53 [Music]', '1:56 the slippers were going everywhere', '1:58 [Music]', '2:01 she would spit at you she would slap her', '2:04 belly to tell you to go away', '2:05 [Music]', "2:08 that's what we want to see in our seals", "2:10 at the shows that they're becoming more", "2:11 wild because so they're stay away from", '2:13 me', '2:16 but that meant that she really had that', '2:18 fighting spirit', "2:22 seeing that shows us that she's going to", '2:24 compete well in the wild and we felt', '2:26 confident in putting her in the pool', '2:27 with the other seals', '2:33 [Music]', '2:37 chili Pika is looking good and healthy', "2:40 he's about 13 kilos now so she's gonna", '2:43 join our other seals out in the pools', '2:45 today', '2:48 as we carried her out she was looking', '2:51 around quite curious and excited', '2:55 and so hilly Pika is ready to go join', "2:58 our other seals in rockpool that's the", '3:02 first time that they actually come in', '3:03 contact with other seals and care so', "3:05 that's really special because since they", "3:07 are social animals it's like a little", "3:08 kid's first day at school", '3:10 [Music]', '3:13 she scooted out and into the water', '3:16 [Music]', "3:21 so that's really Pika joining Pangolin", '3:25 the two of them had a little interaction', '3:27 they had a little smell of each other', '3:30 and then they both had a swim around', '3:33 getting used to their pool and how much', '3:35 space the both of them would have oh', "3:38 there's another friend the pools are the", '3:41 last stage of rehab', "3:43 this is where they're gonna lift social", '3:45 cues from each other', "3:47 they're going to build up their muscles", "3:48 they're going to learn to compete", '3:50 against other seals', '3:57 started to flourish she was the one that', '4:00 was really in the roost she was getting', '4:01 all the fish', '4:04 instead of one kilo each week she would', '4:06 start to gain about two or three each', '4:08 week which was a great sign', '4:10 Target week for a common seal is 30', '4:12 kilos so once she hits 30 kilos she will', '4:15 be determined ready for the Wild and', "4:17 we're gonna put her out back where she", '4:18 belongs', "4:20 when they're in care we know that", "4:23 they're safe", "4:24 but that's not a replacement for the", '4:27 open ocean', '4:27 [Music]', "4:29 Billy Pica's recovery continues and I", "4:31 know she'll get there in the meantime", "4:33 we're excited that some of our other", '4:34 seals are ready to return to the wild', "4:38 I've seen them go back into the wild", "4:40 it's a Bittersweet feeling you know", "4:42 you've been with this puff towards the", '4:44 start of its life', "4:46 I'm for them to finally be released back", "4:49 home it's an amazing feeling", '4:54 thank you', '4:56 foreign', "4:59 ature once they're released you can see", '5:02 their instincts kick in', '5:05 [Music]', '5:09 when they enter the sea you know this is', "5:12 where they're meant to be", '5:17 there is only about', '5:20 that was left in Ireland and the numbers', '5:21 are on a decline and that is due to', '5:24 habitat loss loss of their food source', '5:26 and climate change causing more and more', '5:29 illnesses', '5:32 thing that we can all do is protect', '5:34 their habitat to do our part to fight', '5:36 climate change and to promote a future', "5:39 that seals won't need to be rescued", '5:52 [Music]']
    generate_timestamps(transcript, video_duration)
    #print(transcript)






