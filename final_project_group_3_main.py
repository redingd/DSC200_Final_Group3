import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download("punkt_tab")
nltk.download('stopwords')


# this page has 4 urls I am interested in going to, but this page is only useful for getting these 4 urls - these urls
# take you to the available apartment listings for each apartment building
# using beatuifulsoup and requests to parse the page
url = "https://griffisresidential.com/communities/washington/"
page_ = requests.get(url)
parsed_page = BeautifulSoup(page_.content, "html.parser")
# getting the 4 urls I am interested in going to by using find_all
pages = parsed_page.find_all("a", class_="spaces-button spaces-button-fill-brand")
pg = []
i = 0
# putting the actual urls into a list by using get("href")
while i < 4:
    pg.append(pages[i].get("href"))
    i += 1
# the names of the apartment buildings are belltown, lake washington, north creek, waterfront
# LAKE WASHINGTON IS DIFFERENT

# setting up a bunch of empty lists to fill later
building_name = []
street_address = []
zip_code = []
phone_number = []
num_beds = []
num_baths = []
floor_plan = []
sq_ft = []
base_rent = []
retail_rent = []
length_rental = []
available_rent = []
sentence = []
amenities = []
j = 0
while j < 4:
    # the list of urls is in alphabetical order. Much of the html on this website is organized alphabetically by either
    # the name of the apartment building or the name of the floor plan
    url = pg[j]
    # using beautifulsoup and requests to parse the pages
    pge = requests.get(url)
    prsdpg = BeautifulSoup(pge.content, "html.parser")
    # the 2nd url in the list of the 4 urls of the apartment buildings is for the lake washington building. This page is
    # organized differently than the other 3 pages for the other apartment buildings, so there had to be 2 different
    # scripts depending on the page. Lake Washington will always be the 2nd element in the list, because they organized
    # the first page I scraped alphabetically
    if j == 1:
        # finding all of the available apartments using find_all, looking for articles with a certain attribute
        apts = prsdpg.find_all("article", attrs={"data-spaces-community": "Griffis Lake Washington"})
        # going through every apartment I just found to fill the lists I made earlier
        for apt in apts:
            # appending the name of the building, looking for a div with a certain class name, getting the text and stripping
            # it of whitespace at the ends to make cleaning slightly easier; stripping it could have been done later
            # I am doing apt.find because it is for each individual apartment
            building_name.append(apt.find("div",
                                          class_="spaces-unit-attributes-attribute spaces-unit-attribute-community").text.strip())
            # assigning the street address to a variable to use it to pull the zip code off later, finding street address
            # by looking for links with a certain class name - this uses the full page and not the individual apartment
            # because this is at the bottom of the page and not inside each apartment's article
            address = prsdpg.find("a", class_="ecs_a ecs_address ecs_property_top_item").text.strip()
            street_address.append(address)
            # # appending the zip code by looking for 5 numbers, first one is 9, because all king county zip codes start
            # with 9, and one of the addresses has an address number that is 5 numbers long and starts with a 2. findall
            # of a regular expression gives a list (in this case a list of length 1), and I just need the first (only)
            # element of it
            zip_code.append(re.findall("9[0-9][0-9][0-9][0-9]", address)[0])
            # appending the phone number, looking for a link with a certain class name, getting the text of it - this
            # uses the full page and not the individual apartment, because this is at the bottom of the page and not
            # inside each apartment's article
            phone_number.append(prsdpg.find("a", class_="ecs_a ecs_phone ecs_property_top_item").text)
            # appending the number of beds, baths, and the name of the floor plan by looking for divs with a certain
            # class name
            num_beds.append(apt.find("div",
                                     class_="spaces-unit-attributes-attribute spaces-unit-attribute-bedrooms").text.strip())
            num_baths.append(apt.find("div",
                                      class_="spaces-unit-attributes-attribute spaces-unit-attribute-bathrooms").text.strip())
            floor_plan.append(
                apt.find("div", class_="spaces-unit-attributes-attribute spaces-unit-attribute-plan").text.strip())
            # some of the apartments list a range of square feet instead of just one area, e.g. 567 - 789, so I am
            # splitting it using whitespace as a delimiter and just taking the first number and appending that to my
            # list of square feet
            square_feet = apt.find("div",
                                   class_="spaces-unit-attributes-attribute spaces-unit-attribute-area").text.strip()
            sq_ft.append(square_feet.split()[0])
            # retail rent was the price that the apartment will actually be rented for and includes utilities, and I am
            # appending this to my list of retail rents by looking for a link with a certain class and getting the text
            # and stripping that of whitespace at the start and end of it
            retail_rent.append(apt.find("a",
                                        class_="spaces-text-p-link spaces-text-p-lg-bold spaces-color-content-brand-1-on-ui spaces-color-brand-1-hover spaces__opener").text.strip())
            # base rent is rent without utilities included, appending this by looking for a span with a certain class,
            # getting the text and stripping it
            base_rent.append(apt.find("span",
                                      class_="spaces-text-p-s-default spaces-color-content-2 spaces-unit-base-price").text.strip())
            # this is how long the lease will last in months - usually around 12-15 months, appending it by looking for
            # a span with a certain class and a certain attribute, because available_rent also uses the same class but
            # has a different attribute, and I'm just getting the text for this one
            length_rental.append(
                apt.find("span", class_="spaces-text-p-s-default spaces-color-content-2 spaces-default-lease-term",
                         attrs={"data-spaces-control": "unit-default-lease-term"}).text)
            # this is when the apartment will be available to rent, many are available now, but some will be available
            # on a certain day appending it by looking for a span with a certain class and a certain attribute, because
            # length_rental also uses the same class but has a different attribute, and I'm getting the text and
            # stripping it
            available_rent.append(
                apt.find("span", class_="spaces-text-p-s-default spaces-color-content-2 spaces-default-lease-term",
                         attrs={"data-spaces-control": "unit-default-available-date"}).text.strip())
            # to get a list of amenities, and a descriptive sentence for each apartment I need to go to a different page
            # and the url that this gives gets tacked onto the end of the url for the page of available apartments, so
            # I am using string concatenation and finding a link with a certain class and a certain attributes and
            # getting the link for the new page to scrape; this is a different page for each apartment unit
            url_ = url + apt.find("a", class_="spaces-menu-item",
                                  attrs={"data-spaces-control": "unit-detail-cta"}).get("href")
            # parsing the page using beautifulsoup and requests
            page_ = requests.get(url_)
            prspg = BeautifulSoup(page_.content, "html.parser")
            # list of descriptive sentences to tokenize and remove stopwords on later; looking through the full new page
            # for this, getting the text and stripping it
            sentence.append(prspg.find("div", class_="spaces__detail-description").text.strip())
            # there are several amenities, and I'm finding the list of them using find_all, and then iterating through
            # and just appending the text of them to my list
            amenity = prspg.find_all("li", class_="spaces-li")
            amenity_list = []
            for amnty in amenity:
                amenity_list.append(amnty.text)
            amenities.append(amenity_list)
    # this is for the other pages, which are all laid out the same way
    else:
        # finding all of the available apartments using find_all, looking for divs with a certain class
        apts = prsdpg.find_all("div", class_="spaces-plan-wrapper")
        # going through every apartment I found to fill the lists
        for apt in apts:
            # some of the apartments on this page are unavailable; if unavailable, they won't have a price listed, so
            # if there is a price then the rest of the information I am looking for will be there. Unavailable listings
            # don't have all the same information
            if apt.find("div", class_="spaces-plan-overview-pricing") is not None:
                # appending the name of the building, looking for a div with a certain class name, getting the text and
                # stripping it of whitespace at the ends to make cleaning slightly easier; stripping it could have been
                # done later I am doing prsdpg.find because the name of the apartment is not listed in the same spot as
                # the lake washington page; it is only at the bottom of the page
                building_name.append(prsdpg.find("a", class_="ecs_a ecs_property_top_item ecs_property_name").text)
                # assigning the street address to a variable to use it to pull the zip code off later, finding street
                # address by looking for links with a certain class name - this uses the full page and not the
                # individual apartment because this is at the bottom of the page and not inside each apartment's div
                address = prsdpg.find("a", class_="ecs_a ecs_address ecs_property_top_item").text.strip()
                street_address.append(address)
                # # appending the zip code by looking for 5 numbers, first one is 9, because all king county zip codes
                # start with 9, and one of the addresses has an address number that is 5 numbers long and starts with a
                # 2. findall of a regular expression gives a list (in this case a list of length 1), and I just need the
                # first (only) element of it
                zip_code.append(re.findall("9[0-9][0-9][0-9][0-9]", address)[0])
                # appending the phone number, looking for a link with a certain class name, getting the text of it.
                # This uses the full page and not the individual apartment, because this is at the bottom of the page
                # and not inside each apartment's div
                phone_number.append(prsdpg.find("a", class_="ecs_a ecs_phone ecs_property_top_item").text)
                # appending the number of beds, baths, and the name of the floor plan by looking for divs with a certain
                # class name
                num_beds.append(apt.find("div",
                                         class_="spaces-plan-overview-attribute spaces-plan-overview-attribute-bed-count").text.strip())
                num_baths.append(apt.find("div",
                                          class_="spaces-plan-overview-attribute spaces-plan-overview-attribute-bath-count").text.strip())
                floor_plan.append(apt.find("div", class_="spaces-plan-name").text.strip())
                # some of the apartments list a range of square feet instead of just one area, e.g. 567 - 789, so I am
                # splitting it using whitespace as a delimiter and just taking the first number and appending that to my
                # list of square feet
                square_feet = apt.find("div",
                                       class_="spaces-plan-overview-attribute spaces-plan-overview-attribute-area").text.strip()
                sq_ft.append(square_feet.split()[0])
                # retail rent was the price that the apartment will actually be rented for and includes utilities, and I
                # am appending this to my list of retail rents by looking for a div with a certain class and getting the
                # text and stripping that of whitespace at the start and end of it
                retail_rent.append(
                    apt.find("div", class_="spaces-plan-overview-pricing-primary-price").text.strip())
                # base rent is rent without utilities included, appending this by looking for a div with a certain
                # class, getting the text and stripping it
                base_rent.append(
                    apt.find("div", class_="spaces-plan-overview-pricing-detail-secondary-price").text.strip())
                # the length of the rental has a pretty common class name for this webpage, so I looked for the more
                # uniquely named div that it is inside of, and looked for the 2 spans inside it - the first was a price,
                # so I needed the 2nd one to append to the list of how long the lease is
                outer_div = apt.find("div", class_="spaces-plan-overview-pricing-details")
                length = outer_div.find_all("span", class_="spaces-color-content-2 spaces-text-p-s-default")
                length_rental.append(length[1].text.strip())
                # to get the descriptive sentence to tokenize and remove the stopwords from later I needed to go to a
                # different webpage, and the url that this will give me just gets stuck on the end of the current url,
                # so I just used string concatenation and found a link with a certain class and got the link
                url_ = url + apt.find("a", class_="spaces-button spaces-button-fill-brand").get("href")
                # parsing the new page for every unit with requests and beautifulsoup
                page_ = requests.get(url_)
                prspg = BeautifulSoup(page_.content, "html.parser")
                # list of descriptive sentences to tokenize and remove stopwords on later; looking through the full new
                # page for this, getting the text and stripping it
                sentence.append(prspg.find("div", class_="spaces__detail-description").text.strip())
                # these pages sadly don't have amenities, so to build the dataframe correctly I just added empty strings
                # so they would still be the same length
                amenities.append("")
                # I also had to find the day that they were available to rent on this new page, so I looked through the
                # full page for a span with a certain attribute, got the text, and stripped it
                available_rent.append(
                    prspg.find("span", {"data-spaces-control": "unit-default-available-date"}).text.strip())
    j += 1
# 2 empty lists to populate during cleaning, making the set of stopwords
price_per_sq_ft = []
tokenized_no_stopwords = []
stop_words = set(stopwords.words('english'))
k = 0
# all the lists should be the same length, so it doesn't matter which one I picked, but I'm going through certain lists
# and cleaning them more thoroughly by removing commas, dollar signs, unnecessary words, and whitespace by using the
# replace method - could have also used the regex sub method
while k < len(sq_ft):
    sq_ft[k] = sq_ft[k].replace(",", '')
    retail_rent[k] = retail_rent[k].replace("$", '')
    retail_rent[k] = retail_rent[k].replace(",", '')
    retail_rent[k] = retail_rent[k].replace("From\xa0", '')
    retail_rent[k] = retail_rent[k].replace("\n", '')
    retail_rent[k] = retail_rent[k].replace("\t", '')
    retail_rent[k] = retail_rent[k].replace(" /Mo.", '')
    base_rent[k] = base_rent[k].replace("\n", '')
    base_rent[k] = base_rent[k].replace("\t", '')
    base_rent[k] = base_rent[k].replace("Base Rent", '')
    base_rent[k] = base_rent[k].replace("$", '')
    base_rent[k] = base_rent[k].replace(",", '')
    available_rent[k] = available_rent[k].replace("\n", '')
    available_rent[k] = available_rent[k].replace("\t", '')
    available_rent[k] = available_rent[k].replace("Avail.", '')
    length_rental[k] = length_rental[k].replace(" Mo.", '')
    # making a column of price per square foot after cleaning the columns it will be based off of and turning them into
    # integers - using the round method to round to 2 digits, because there's only 100 cents in a dollar, and it doesn't
    # make sense to have more accuracy than what you could pay
    price_per_sq_ft.append(round(int(base_rent[k]) / int(sq_ft[k]), 2))
    # doing the tokenization similarly to how it was performed in the in-class slides
    word_tokens = word_tokenize(sentence[k])
    inner_list = []
    for w in word_tokens:
        if w not in stop_words:
            inner_list.append(w)
    tokenized_no_stopwords.append(inner_list)
    k += 1
# making a dictionary to build the dataframe from using many of my lists I just populated
data = {"Building Name": building_name, "Street Address": street_address, "Zip Code": zip_code,
        "Phone Number": phone_number, "Number of Beds": num_beds, "Number of Baths": num_baths,
        "Floor Plan": floor_plan, "Square Feet": sq_ft, "Base Rent": base_rent,
        "Availability of Apartment": available_rent, "Rent with Utilities": retail_rent, "Length of Rental (Months)": length_rental,
        "Tokenized Sentences with no stopwords": tokenized_no_stopwords, "Price per Square Foot": price_per_sq_ft,
        "Amenities": amenities}
df = pd.DataFrame(data)
df.set_index("Zip Code")
# changing some types to better suit what data they're actually holding instead of keeping them as strings
df.astype({"Square Feet": int, "Base Rent": int, "Length of Rental (Months)": int, "Rent with Utilities": float, "Price per Square Foot": float})


headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI2IiwianRpIjoiOTlmZDhlZWQyNjBjM2FiNzA"
                     "yODk4N2Q3ZWQ0YTNhMWZkNzYwMmViZGY3OGIzYjliNmY0ZDBlMGQ2NjE2ZDM2NjM2ZDcyZTJkY2E4MmJlOGYiLCJpYX"
                     "QiOjE3NjQzNjA1NTEuNjY2MDUxLCJuYmYiOjE3NjQzNjA1NTEuNjY2MDUzLCJleHAiOjIwNzk4OTMzNTEuNjYyMDM5LC"
                     "JzdWIiOiIxMTM5OTkiLCJzY29wZXMiOltdfQ.n5fyBniANFm-DJkZ4JFLeo0uDCEh12NfV7j-g-q-GOsxy83JG-obl"
                     "J-kT7tT3x53vBAG4MfuMV_YjUOUp0LVOg"}

# the identifier of king county washington is 5303399999
url = "https://www.huduser.gov/hudapi/public/fmr/data/5303399999"
request = requests.get(url, headers=headers)
data = request.json()
# data is the key for the rest of the json object
outer = data.get("data")

# the values not paired with the basicdata key are not very useful for getting the fmr of each zip code
# they mostly just clarify what county you asked for and if it is a metro area or a small area, so I used the data
# from the basicdata key to build the pandas df
inner = outer.get("basicdata")

# building the pandas df, setting the index to zip code
data_pd = pd.DataFrame(inner)
data_pd.set_index("zip_code")
data_pd.rename(columns={"zip_code": "Zip Code"}, inplace=True)


# outer join of the api and scraped datasets, joining on the zip code because that is the column that they have in common
merged_api_and_scrape = pd.merge(df, data_pd, on="Zip Code", how="outer")
merged_api_and_scrape.to_csv("./api_and_scrape.csv")
