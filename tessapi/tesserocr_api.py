from tesserocr import PyTessBaseAPI, RIL, iterate_level

with PyTessBaseAPI() as api:
    api.SetImageFile('/home/jkamlah/Coding/tesseract/testing/eurotext.tif')
    api.SetVariable("save_blob_choices", "T")
    api.SetRectangle(37, 228, 548, 31)
    api.Recognize()

    ri = api.GetIterator()
    level = RIL.SYMBOL
    for r in iterate_level(ri, level):
        symbol = r.GetUTF8Text(level)  # r == ri
        conf = r.Confidence(level)
        if symbol:
            print(u'symbol {}, conf: {}'.format(symbol, conf))
        indent = False
        ci = r.GetChoiceIterator()
        for c in ci:
            if indent:
                print('\t\t ')
            print('\t- ')
            choice = c.GetUTF8Text()  # c == ci
            print(u'{} conf: {}'.format(choice, c.Confidence()))
            indent = True
        print('---------------------------------------------')





from tesserocr import PyTessBaseAPI,PSM, OEM, RIL,iterate_level

images = ['/media/sf_ShareVB/many_years_firmprofiles/short/1973/0105_1973_230-6_B_066_0213.jpg','/home/jkamlah/Coding/tesseract/testing/eurotext.tif']
images = ['/home/jkamlah/Coding/tesseract/testing/eurotext.tif']

with PyTessBaseAPI(psm=PSM.SINGLE_COLUMN, oem=OEM.LSTM_ONLY, lang="deu") as api:
    for img in images:
        api.SetImageFile(img)
        api.SetVariable("save_blob_choices", "1")
        api.Recognize()

        ri = api.GetIterator()
        level = RIL.SYMBOL
        for r in iterate_level(ri, level):
            symbol = r.GetUTF8Text(level)  # r == ri
            conf = r.Confidence(level)
            if symbol:
                print(u'symbol {}, conf: {}'.format(symbol, conf))
                indent = False
            ci = r.GetChoiceIterator()
            #font = r.WordIsNumeric()
            #for c in iterate_choices(ci):
             #   print(c.Confidence())
            for c in ci:
                if indent:
                    print('\t\t ')
                print('\t- ')
                choice = c.GetUTF8Text() # c == ci
                print(u'{} conf: {}'.format(choice, c.Confidence()))
                indent = True
            print('---------------------------------------------')