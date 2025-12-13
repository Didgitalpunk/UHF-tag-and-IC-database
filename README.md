# UHF-tag-and-IC-database
This repo is a collection of datasheets, tools, programs, and other, related to UHF RFID.
most notably, there's three main things:

- [Digits' mdid list](https://github.com/Didgitalpunk/UHF-tag-and-IC-database/blob/main/Digits'_mdid_list.json), a deeper version of the MDID list from GS1, with corrected website links, extra info on the chips, and most importantly, TMNs for all the chips I could get info on! This list is regularly updated through research, new chip acquisitions, new MDID list entries from GS1 themselves, etc. if you want to contribute, don't hesitate to contact me, or make a pull request! 

- [The mdid search engine](https://github.com/Didgitalpunk/UHF-tag-and-IC-database/blob/main/MDID_Search_Engine.py), which allows you to type in a TID and see what info is contained automatically by searching [digits' mdid list](https://github.com/Didgitalpunk/UHF-tag-and-IC-database/blob/main/Digits'_mdid_list.json) and returning what it finds, as well as decoding which GS1 TDS options are enabled. this requires the Digits'_mdid_list.json to be present in the same directory to work.

- [The TID encoder](https://github.com/Didgitalpunk/UHF-tag-and-IC-database/blob/main/TID%20encoder.py), which allows you to generate a TID that strictly follows GS1's TDS (Tag Data Standard), either for testing, or for using in certain scenarios.


## Acknowledgements and links

 - [GS1 website](https://www.gs1.org/)
 - [GS1 tools](https://www.gs1.org/services)
 - [latest TDS](https://ref.gs1.org/standards/tds/)

Thank you to all the folks that follow this page and use its contents! You are the reason I keep working on this and maintain this repo!

Thank you to the folks over on the Iceman and Flipper zero discord for the good vibes that make working on this stuff more than worth it!

And lastly, thank you to the folks at GS1 for the super quick and professional support when I've needed more info and had feedback for them!
