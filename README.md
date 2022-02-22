# Getting Lego set price from Bricklink

My Lego set collection is stored in my profile on [brickset.com](https://brickset.com) and this website allows you to download your collection in a CSV file. It gives you lots of information for each Lego set you own but it does not tell you what is their current price.

[Bricklink](https://bricklink.com) is a marketplace for new and used Lego sets. On each Lego set page, you can retrieve the 6 months average price for a set in new condition. I wrote a script that takes as input the CSV file provided by Brickset and fetches the current price of each Lego set.

To use this script:

```sh
$ ./scrape.py <lego-collection-csv>
```

All prices displayed are in euros.

