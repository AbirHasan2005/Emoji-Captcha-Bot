# (c) @AbirHasan2005 &

async def MakeCaptchaMarkup(markup, __emoji, indicator):
    __markup = markup
    for i in markup:
        for k in i:
            if k["text"] == __emoji:
                k["text"] = f"{indicator}"
                k["callback_data"] = "HeHe"
                return __markup
