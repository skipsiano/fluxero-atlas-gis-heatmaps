import folium  
uk_map = folium.Map(location=[55.3781, -3.4360], zoom_start=6)  
uk_map.save("index.html")  
print("Success!") 
