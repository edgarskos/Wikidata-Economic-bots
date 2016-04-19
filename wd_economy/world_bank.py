import csv
import pywikibot


class Database(object):
    """docstring for Database"""
    def __init__(self, path):
        # super(Database, self).__init__()
        self.file = open(path, 'r')
        self.country_marker = 'Country Name'
        self.year_marker = '2014'
        self.real_data = []

    def parse_database(self):
        i_of_country = None
        i_of_year = None
        with self.file as f:
            reader = csv.reader(f, quotechar='"')
            for line in reader:
                if not line:
                    continue
                if ',' in line[0]:
                    print(line[0])
                for i in range(len(line)):
                    line[i] = line[i].replace('"', '')
                    if line[i] == self.country_marker:
                        i_of_country = i
                    elif line[i] == self.year_marker:
                        i_of_year = i
                if i_of_year is not None and i_of_country is not None:
                    if line[i_of_year] == self.year_marker:
                        continue
                    self.real_data.append(Country(line[i_of_country],
                                          line[i_of_year]))
            if not self.real_data:
                raise RuntimeError('It seems I could not harvest any data :(')


class Country(object):
    """docstring for Country"""
    def __init__(self, name, data):
        super(Country, self).__init__()
        self.name = name
        if data:
            self.data = int(round(float(data)))
        else:
            self.data = None

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if hasattr(other, 'name'):
            return self.name == other.name
        return self.name == other

    def find_item(self):
        site = pywikibot.Site('en')
        print(site)
        page = pywikibot.Page(site, self.name)
        try:
            item = pywikibot.ItemPage.fromPage(page)
        except pywikibot.NoPage:
            return None

        # Worst kind of check :|
        if '3624078' in str(item._content) or '6256' in str(item._content):
            return item


class Bot(object):
    """docstring for Bot"""
    def __init__(self, path, url, p_number, unit='Q4917', error=1):
        super(Bot, self).__init__()
        self.db = Database(path)
        self.url = url
        self.p_number = p_number
        self.unit = unit
        self.error = error
        site = pywikibot.Site('en')
        self.repo = site.data_repository()

    def run(self):
        self.db.parse_database()
        print(self.db.real_data[0])
        for country in self.db.real_data:
            if not country.data:
                print('Data is not avaliable for that '
                      'year for %s' % country.name)
                continue
            item = country.find_item()
            if not item:
                print('It seems I can not find item for '
                      'country {0}. Skipping'.format(country.name))
                continue
            if self.p_number in item.claims:
                print(item.claims[self.p_number][0].references)
                print('It seems this item already have that data. '
                      'I will not change anything')
                continue
            unit_url = "http://www.wikidata.org/entity/%s" % self.unit
            snak = {"mainsnak":
                    {"snaktype": 'value',
                     "property": self.p_number,
                     "datavalue": {
                        "value": {
                            "amount": country.data,
                            "unit": unit_url,
                            "upperBound": country.data + self.error,
                            "lowerBound": country.data - self.error
                            },
                        "type": "quantity"},
                     "datatype": "quantity"},
                    "type": "statement",
                    "rank": "normal"}
            try:
                item.editEntity(data={'claims': [snak]})
            except:
                continue
            item.get(force=True)
            source = pywikibot.Claim(self.repo, 'P854')
            source.setTarget(self.url)
            qual = pywikibot.Claim(self.repo, 'P585')
            year_target = pywikibot.WbTime(year=int(self.db.year_marker))
            qual.setTarget(year_target)
            if self.p_number not in item.claims:
                continue
            item.claims[self.p_number][0].addSource(source)
            item.claims[self.p_number][0].addQualifier(qual)
