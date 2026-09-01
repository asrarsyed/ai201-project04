"""
Test data for scripts/run_eval.py, grouped into scenarios that line up with
the five criteria in docs/REQUIREMENTS.md:

  1. "my own writing"  -> Criterion 1 (false positives)
  2. "human vs ai"     -> Criterion 2 (score spread) and Criterion 3 (label
                          coverage). The 10 samples from scenario 1 plus 5
                          AI-generated samples from one prompt.
  3. "bad input"       -> Criterion 5 (missing, empty, or oversized text)
  4. "appeal path"     -> Criterion 4. A "kind": "appeal" scenario, which
                          submits, appeals straight away, then checks that
                          the status changed and an appeal entry was logged.

One note on the data: the 10 "my own writing" samples are real human writing
taken from the public C4 dataset (huggingface.co/datasets/allenai/c4). They
were not written by hand for this project. See docs/RESEARCH.md.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # NOT actually my own writing. See the note in the module docstring
        # above. These come from allenai/c4, which is real human web text,
        # and were used because I did not have my own writing ready in time
        # for this run.
        "texts": [
            "Reclusive and isolated social groups, with specific rules and a tendency for confinement are certainly the center of Lanthimos movies. He uses his actors in an innovative way, directing them to play as unrealistically as possible, in a way that reminds us of marionettes or robots who are not yet really aware of the element of speech and thought. Every frame is designed and stylized strictly, to a great extent where the camera stays motionless in space, after being set in a carefully thought-out position, where the only movement comes from the actors playing in the scene. In this unorthodox way Lanthimos is trying to introduce us to his unique utopian environments and isolated social groups.",
            "Do you want to get better at making delicious BBQ? You will have the opportunity, put this on your calendar now. Thursday, September 22nd join World Class BBQ Champion, Tony Balay from Lonestar Smoke Rangers. He will be teaching a beginner level class for everyone who wants to get better with their culinary skills. He will teach you everything you need to know to compete in a KCBS BBQ competition, including techniques, recipes, timelines, meat selection and trimming, plus smoker and fire information. The cost to be in the class is $35 per person, and for spectators it is free. Included in the cost will be either a t-shirt or apron and you will be tasting samples of each meat that is prepared.",
            "The highly anticipated PBS Kids in the Park festival is tomorrow, Saturday, June 21. But there are lot of other events for families to enjoy this weekend as well. Also on Saturday, check out the free Summer Solstice Celebration at the Indianapolis Museum of Art's 100 Acre Woods. The Windsor Park Neighborhood Association will also celebrate the solstice with a festival in Fletcher Park from 12 p.m.-11 p.m. Saturday and Sunday, you can experience Native American culture through myriad experiences on offer at the Eiteljorg Indian Market and Festival. Saturday, the Irvington Folk Festival features its Children's Day from 11 a.m.-2 p.m. at Ellenberger Park.",
            "I figured if I could do it at all, I needed the help of the big guns. My 400mm f/2.8 lens would have worked nicely, it would allow me to zoom into the moon to fill the frame and still let plenty of light in to give me the best chance of a capture. I ran into two problems. First off, doubled – the 400mm 2.8 lens goes to 800mm f/5.6. Then, the more zoomed in you are, the more the movement of the subject in the frame. I had settled on a 1.4x extender which would get me close to 600mm with just a one stop penalty to put me at f/4. Next was the camera. I have a Canon Rebel 35mm film SLR that I bought on eBay for $1.",
            "The article itself is pretty cut and dry, a bunch of butthurt dumb asses complaining to their superiors. What's interesting is the response their superiors gave. Which I have the pleasure of showing you. This is in response to the New Year's Eve hack of the California Statewide Law Enforcement Association website by Anonymous, a loose knit band of cyber experts who have gained access to other law enforcement association sites including PORAC and many other international corporations. Thats the first paragraph now let me narrow down the interesting part. Remember when they used to call us a bunch of teenagers that have a bit of motivation but can't do anything? To think how much they change their tones, they now know the truth.",
            'Why is it important to learn horsemanship besides learning to ride? Safety is one very important reason - but also to have an enjoyable time together with your horse and not the fearful, exhausting fight because the horse and rider do not communicate well. We often blame the horse, but in reality we are to blame, since in most cases it is lack of communication skills from the person, who does not speak "horse". When people ask me: My horse is bucking with me, can you fix it? I answer with another question: When and why do yo think your horse is bucking?',
            "So, apparently the info I found about how tables start was wrong. At least one game didn't start despite having over the min number of players... Sorry. I started a new RftG, and invited the people I think were interested. If I invited you by mistake, sorry, don't feel obligated to play, and if I missed you, double sorry. I hope this system is the next thing the admins decide to overhaul. I'll try the other failed ones again soon. New game! Nippon is open for 3 others to join here. I've never played it before, but looking forward to learning.",
            "The competition is open to all people from any country. Our primary focus is one of the most important issues we face in our times – banishing violence and inspiring people to encounter each other in a peaceful manner. The main idea is to use our creative fantasy to make clearly formulated statements against violence. This approach gives all participants a chance to put their own abilities on display with compelling and fascinating creative works which set new standards. Valuable prizes and media coverage serve as an incentive.",
            "I don't know how the car started! I didn't turn it on. You guys saw me! How did the car start? Lees how did your car start huh? You killed Pete Von Horn, Charlie you killed him! Go ahead tell us steve! My theme is Fear and suspicion are destructive forces. Evidence one supports my theme because they blamed him because the car turned on by itself, when he went into the car. After that they get mad and asked why his car turned on and the other cars didn't.",
            "How to unlock iphone 6 plus (ios9.1) after successful jailbrken? Today, I have successfully jailbroken my iPhone 6 Plus (ios 9.1) using Pangu 9 v 1.3.1....I want my phone to e network unlocked..Currently its is locked to sprint, How can I unlock this phone to use another carrier such as AT&T sim card? Which Cydia App or whats the process to unlock the iphone after it has been jailbroken? You can contact Sprint and ask them to unlock it for you, if you meet the qualifications for unlocking.",
        ],
    },
    {
        "name": "human vs ai",
        "criterion": "2, 3",
        # The first 10 are the same "my own writing" set above, since
        # Criterion 2 reuses it. The last 5 come from one prompt ("Write a
        # short paragraph about the benefits of regular exercise.") pasted
        # into a chatbot five times. Those are genuinely AI-generated,
        # because that is what this half of the criterion is testing.
        # Together the 15 samples run from clearly human to clearly AI, which
        # is also what Criterion 3 (label coverage) reads.
        "texts": [
            "Reclusive and isolated social groups, with specific rules and a tendency for confinement are certainly the center of Lanthimos movies. He uses his actors in an innovative way, directing them to play as unrealistically as possible, in a way that reminds us of marionettes or robots who are not yet really aware of the element of speech and thought. Every frame is designed and stylized strictly, to a great extent where the camera stays motionless in space, after being set in a carefully thought-out position, where the only movement comes from the actors playing in the scene. In this unorthodox way Lanthimos is trying to introduce us to his unique utopian environments and isolated social groups.",
            "Do you want to get better at making delicious BBQ? You will have the opportunity, put this on your calendar now. Thursday, September 22nd join World Class BBQ Champion, Tony Balay from Lonestar Smoke Rangers. He will be teaching a beginner level class for everyone who wants to get better with their culinary skills. He will teach you everything you need to know to compete in a KCBS BBQ competition, including techniques, recipes, timelines, meat selection and trimming, plus smoker and fire information. The cost to be in the class is $35 per person, and for spectators it is free. Included in the cost will be either a t-shirt or apron and you will be tasting samples of each meat that is prepared.",
            "The highly anticipated PBS Kids in the Park festival is tomorrow, Saturday, June 21. But there are lot of other events for families to enjoy this weekend as well. Also on Saturday, check out the free Summer Solstice Celebration at the Indianapolis Museum of Art's 100 Acre Woods. The Windsor Park Neighborhood Association will also celebrate the solstice with a festival in Fletcher Park from 12 p.m.-11 p.m. Saturday and Sunday, you can experience Native American culture through myriad experiences on offer at the Eiteljorg Indian Market and Festival. Saturday, the Irvington Folk Festival features its Children's Day from 11 a.m.-2 p.m. at Ellenberger Park.",
            "I figured if I could do it at all, I needed the help of the big guns. My 400mm f/2.8 lens would have worked nicely, it would allow me to zoom into the moon to fill the frame and still let plenty of light in to give me the best chance of a capture. I ran into two problems. First off, doubled – the 400mm 2.8 lens goes to 800mm f/5.6. Then, the more zoomed in you are, the more the movement of the subject in the frame. I had settled on a 1.4x extender which would get me close to 600mm with just a one stop penalty to put me at f/4. Next was the camera. I have a Canon Rebel 35mm film SLR that I bought on eBay for $1.",
            "The article itself is pretty cut and dry, a bunch of butthurt dumb asses complaining to their superiors. What's interesting is the response their superiors gave. Which I have the pleasure of showing you. This is in response to the New Year's Eve hack of the California Statewide Law Enforcement Association website by Anonymous, a loose knit band of cyber experts who have gained access to other law enforcement association sites including PORAC and many other international corporations. Thats the first paragraph now let me narrow down the interesting part. Remember when they used to call us a bunch of teenagers that have a bit of motivation but can't do anything? To think how much they change their tones, they now know the truth.",
            'Why is it important to learn horsemanship besides learning to ride? Safety is one very important reason - but also to have an enjoyable time together with your horse and not the fearful, exhausting fight because the horse and rider do not communicate well. We often blame the horse, but in reality we are to blame, since in most cases it is lack of communication skills from the person, who does not speak "horse". When people ask me: My horse is bucking with me, can you fix it? I answer with another question: When and why do yo think your horse is bucking?',
            "So, apparently the info I found about how tables start was wrong. At least one game didn't start despite having over the min number of players... Sorry. I started a new RftG, and invited the people I think were interested. If I invited you by mistake, sorry, don't feel obligated to play, and if I missed you, double sorry. I hope this system is the next thing the admins decide to overhaul. I'll try the other failed ones again soon. New game! Nippon is open for 3 others to join here. I've never played it before, but looking forward to learning.",
            "The competition is open to all people from any country. Our primary focus is one of the most important issues we face in our times – banishing violence and inspiring people to encounter each other in a peaceful manner. The main idea is to use our creative fantasy to make clearly formulated statements against violence. This approach gives all participants a chance to put their own abilities on display with compelling and fascinating creative works which set new standards. Valuable prizes and media coverage serve as an incentive.",
            "I don't know how the car started! I didn't turn it on. You guys saw me! How did the car start? Lees how did your car start huh? You killed Pete Von Horn, Charlie you killed him! Go ahead tell us steve! My theme is Fear and suspicion are destructive forces. Evidence one supports my theme because they blamed him because the car turned on by itself, when he went into the car. After that they get mad and asked why his car turned on and the other cars didn't.",
            "How to unlock iphone 6 plus (ios9.1) after successful jailbrken? Today, I have successfully jailbroken my iPhone 6 Plus (ios 9.1) using Pangu 9 v 1.3.1....I want my phone to e network unlocked..Currently its is locked to sprint, How can I unlock this phone to use another carrier such as AT&T sim card? Which Cydia App or whats the process to unlock the iphone after it has been jailbroken? You can contact Sprint and ask them to unlock it for you, if you meet the qualifications for unlocking.",
            "Regular exercise offers a wide range of benefits for both physical and mental health. Engaging in consistent physical activity helps strengthen the cardiovascular system, improve muscle tone, and maintain a healthy body weight. Beyond the physical advantages, exercise has been shown to reduce stress, anxiety, and symptoms of depression by triggering the release of endorphins, the body's natural mood elevators. Additionally, regular movement can improve sleep quality, boost energy levels, and enhance overall cognitive function. By incorporating exercise into a daily routine, individuals can experience improvements in both their physical well-being and their overall quality of life.",
            "Regular exercise is one of the most effective ways to maintain long-term health and wellness. It strengthens the heart, improves circulation, and helps regulate blood sugar and cholesterol levels, reducing the risk of chronic diseases such as diabetes and heart disease. Exercise also plays a critical role in mental health, helping to alleviate symptoms of stress and anxiety while promoting better focus and emotional stability. Furthermore, staying physically active supports healthy aging by preserving bone density, muscle mass, and joint flexibility. Making exercise a consistent part of one's lifestyle can lead to significant improvements in both physical resilience and mental clarity.",
            "Exercising on a regular basis provides numerous benefits that extend far beyond physical fitness. It helps build stronger muscles and bones, supports a healthy immune system, and can significantly lower the risk of developing conditions like obesity, high blood pressure, and heart disease. On the mental side, physical activity is known to reduce feelings of anxiety and depression while improving mood and self-esteem. It can also enhance sleep patterns and increase overall energy throughout the day. Whether through walking, running, or strength training, regular movement is a simple yet powerful investment in a longer, healthier life.",
            "There are many compelling reasons to make regular exercise a part of everyday life. Physically, it improves cardiovascular endurance, builds muscular strength, and helps the body maintain a healthy weight over time. Mentally, exercise has a powerful effect on reducing stress and improving overall emotional well-being, largely due to the endorphins released during physical exertion. It can also sharpen concentration, boost memory, and contribute to better sleep quality. Ultimately, consistent physical activity is one of the simplest and most accessible ways to support both a healthy body and a healthy mind.",
            "Regular physical activity brings substantial benefits to both the body and the mind. It helps improve heart health, build endurance, and maintain a healthy weight, while also lowering the risk of numerous chronic illnesses. Exercise is equally valuable for mental health, as it can reduce anxiety, elevate mood, and provide a natural outlet for managing daily stress. In addition, staying active often leads to improved sleep and higher energy levels, creating a positive cycle that supports overall wellness. Making time for regular exercise, even in small amounts, can have a lasting positive impact on quality of life.",
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_bad_missing"},  # no text field at all
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "   ", "creator_id": "eval_bad_whitespace"},
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
        ],
    },
    {
        "name": "appeal path",
        "criterion": 4,
        "kind": "appeal",
        # Each item gets submitted, then appealed straight away. The
        # appeal-scenario code in run_eval.py checks two things: did the
        # status move off "decided", and did an "appeal" event land in the
        # log for that content_id.
        "texts": [
            "This is a genuine submission from a real writer who intends to appeal the decision regardless of what label comes back, purely to exercise the appeal path.",
            "A second independent submission, written specifically to test that appeals are recorded reliably and that each one gets its own audit trail entry.",
            "A third piece of ordinary writing, submitted once, then appealed once, to see whether the appeal path behaves the same way every time it's used.",
            "Fourth sample text for the appeal-path scenario, plain and unremarkable, sent through submit and then straight into an appeal.",
            "Fifth and final sample for this scenario, again just ordinary text, used only to confirm the appeal endpoint is consistent across repeated use.",
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed before a long run starts, rather than
    partway through it.

    A "bodies" scenario is left out of the empty check on purpose. An empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion impossible to test.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies. Pick one."
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict. Bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty. If an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
