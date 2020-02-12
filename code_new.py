import requests
import datetime
import urllib
import os
from time import sleep
from bs4 import BeautifulSoup
import mysql.connector
import re
mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="abc"
            )
mycursor = mydb.cursor()
class vidstreaming():
    
    def run(self):        
        url = 'http://vidstreaming.io/'    

        ### To get scrap only the first page just replace 175 with 2 ####
        for total_pages in range(1,175):
            
            page_link = 'http://vidstreaming.io/?page=' + str(total_pages)
            res = requests.get(page_link)
            if res.ok:
                soup = BeautifulSoup(res.text, 'html.parser')
                listing = soup.find('ul',{'class':'listing'})
                if listing:
                    listing_li = listing.find_all('li',{'class':'video-block'})
                    if listing_li:
                        list_array = []
                        li_list = {}
                        for list_li in listing_li:
                            link = 'http://vidstreaming.io' + list_li.find('a')['href']
                            li_list['link'] = link
                            
                            image_anime = list_li.find('div',{'class':'picture'})
                            image_anime_src = image_anime.find('img').get('src')
                            li_list['image_link'] = image_anime_src
                            list_array.append(li_list)
                            li_list = {}
                        

                        ### Looping over links on main page #####
                        
                        image_path = './images/'
                        try:
                            for link_li in list_array:

                                episode_link = link_li.get('link')
                                anime_image_link = link_li.get('image_link')

                                res_inner = requests.get(episode_link)
                                if res_inner:

                                    soup2 = BeautifulSoup(res_inner.text, 'html.parser')
                                    more_lists_array = []
                                    more_lists = soup2.find('ul',{'class':'lists'})
                                    if more_lists:
                                        
                                        more_links = more_lists.find_all('a')
                                        for mor_link in more_links:
                                            new_link = 'http://vidstreaming.io' + mor_link['href']
                                            more_lists_array.append(new_link)

                                    
                                    ##### More episodes code here #####
                                    try:
                                            
                                        if more_lists_array != []:
                                            self.more_episodes(more_lists_array,anime_image_link)

                                    except Exception as e:
                                        print("Exception : ",e)

                        except Exception as ex:
                            print("Exception is: ",ex)
                                        
        
    def more_episodes(self,more_episodes_links,anime_image_link):
        
        image_path = './images/'
        status = 0
        while more_episodes_links:
            
            link_li = more_episodes_links.pop()
            print("Opening Episode Link: ",link_li)
            try:
                res_inner = requests.get(link_li)
            except Exception as ex:
                print("Exception in request link_li : ",link_li)
                res_inner = ''
            sleep(1)
            if res_inner:
                soup2 = BeautifulSoup(res_inner.text, 'html.parser')
                episode_num = link_li.split('-')
                episode_num_f = episode_num[-1]

                synopsis = soup2.find('div',{'id':'rmjs-1'})
                if synopsis:
                    synopsis_f = synopsis.text 
                    synopsis_f = synopsis_f.strip()

                video_det = soup2.find('div',{'class':'video-details'})
                if video_det:
                    name = video_det.find('span',{'class':'date'})
                    if name:
                        name_f = name.text 
                        name_final = name_f.strip()
                        name_f = re.sub(r'[^a-zA-Z0-9_\s]+', '',name_final) 
                        image_name = name_f.replace(' ','-')
                        image_name = image_name.lower()

                if status == 0:
                    try:                                        
                        if '.jpg' in anime_image_link:
                            image_name_ff = image_name + ".jpg"
                            try:
                                urllib.request.urlretrieve(anime_image_link, image_path + image_name_ff)
                                status = 1
                            except:
                                try:
                                    down_link = requests.get(anime_image_link)
                                    with open(image_path + image_name_ff, "wb") as img_obj:
                                        img_obj.write(down_link.content)
                                    status = 1    
                                except Exception as eb:
                                    print("Exception in downloading image: ",eb)
                            image_table_name = '//ani-image.a2zapi.net/anime/' + image_name_ff
                        elif '.png' in anime_image_link:
                            image_name_ff = image_name + ".png"
                            try:
                                urllib.request.urlretrieve(anime_image_link, image_path + image_name_ff)
                                status = 1
                            except:
                                try:
                                    down_link = requests.get(anime_image_link)
                                    with open(image_path + image_name_ff, "wb") as img_obj:
                                        img_obj.write(down_link.content)
                                    status = 1 
                                except Exception as eb2: 
                                    print("Exception in downloading image..",eb2)
                            image_table_name = '//ani-image.a2zapi.net/anime/' + image_name_ff
                        else:
                            image_table_name = ''
                            status = 1
                    except Exception as ex:
                        print("Exception in image downloading... ",ex)
                        image_table_name = ''
                            

                vid = soup2.find('div',{'class':'play-video'})
                if vid:
                    vid_iframe = vid.find('iframe')['src']
                    vid_id = vid_iframe.split('id=')
                    vid_id = vid_id[1].split('&')
                    video_id = vid_id[0]
                    video_id = ''.join(e for e in video_id if e.isalnum())
                    video_id = video_id.strip()

                time_now =  datetime.datetime.now()
                time_now_f = time_now.strftime("%Y-%m-%d %H:%M:%S") 

                ##### Check record already exists or not ######
                try:
                    mycursor.execute("SELECT slug,id, COUNT(*) FROM anime WHERE slug = %s GROUP BY slug", (image_name,))
                    #row_count = mycursor.rowcount
                    row_count = mycursor.fetchall()
                    if row_count:
                        #check_episode
                        for cou in row_count:
                            r_id = cou[1]
                            
                            mycursor.execute("SELECT episode_number,id, COUNT(*) FROM episode_subbed WHERE episode_anime = %s and episode_number = %s GROUP BY episode_number", (r_id,episode_num_f))
                            row_count2 = mycursor.fetchall()
                            ### Episode doesn't exists ###    
                            if not row_count2:
                                print ("It Does Not Exist")
                                
                                try:
                                    last_id = r_id
                                except Exception as ex1:
                                    print("Exception ex: ",ex1)
                                
                                try:
                                    sql1 = "INSERT INTO episode_subbed (episode_anime,episode_number,created) VALUES (%s, %s,%s)"
                                    val1 = (last_id,episode_num_f ,time_now_f)
                                    mycursor.execute(sql1, val1)
                                    mydb.commit()
                                    last_id_ep_subbed = mycursor.lastrowid
                                except Exception as ex2:
                                    print("Exception: ",ex2)

                                try:    
                                    sql2 = "INSERT INTO video_subbed (episode_id,video_id,host,video_type) VALUES (%s, %s,%s,%s)"
                                    val2 = (last_id_ep_subbed ,video_id,'vidstream','subbed')
                                    mycursor.execute(sql2, val2)
                                    mydb.commit()
                                except Exception as ex3:
                                    print("Exception :  ",ex3)
                            else:
                                print("Episode Already exists- Anime Name: " + image_name +  " - Epiosde num: ",episode_num_f)

                    #print ("number of affected rows: {}".format(row_count))
                    if not row_count:
                        print ("It Does Not Exist")
                        try:
                            sql = "INSERT INTO anime (slug,name,synopsis,image,`create`) VALUES (%s,%s,%s,%s,%s)"
                            val = (image_name,name_final,synopsis_f,image_table_name,time_now_f)
                            mycursor.execute(sql, val)
                            mydb.commit()
                            last_id = mycursor.lastrowid
                        except Exception as ex1:
                            print("Exception ex: ",ex1)
                        
                        try:
                            sql1 = "INSERT INTO episode_subbed (episode_anime,episode_number,created) VALUES (%s, %s,%s)"
                            val1 = (last_id,episode_num_f ,time_now_f)
                            mycursor.execute(sql1, val1)
                            mydb.commit()
                            last_id_ep_subbed = mycursor.lastrowid
                        except Exception as ex2:
                            print("Exception: ",ex2)

                        try:    
                            sql2 = "INSERT INTO video_subbed (episode_id,video_id,host,video_type) VALUES (%s, %s,%s,%s)"
                            val2 = (last_id_ep_subbed ,video_id,'vidstream','subbed')
                            mycursor.execute(sql2, val2)
                            mydb.commit()
                        except Exception as ex3:
                            print("Exception :  ",ex3)

                except:
                    print("Sql record check error")

    
if __name__ == "__main__":
    vidstreaming().run()  
