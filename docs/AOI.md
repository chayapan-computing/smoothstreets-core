[[BASEMAP]]

AOI

Mandarin Oriental Hotel, Chao Phraya River
JW Marriot Hotel, Sukhumvit
BMA2 Din Daeng
Kasetsart University
Prince of Songkla, Phuket
Patong City
Pattaya City
Chulalongkorn University
Chocolate Ville
Bangchan Industrial Estate
Mabtapud Industrial Estate
Rayong International Port
Ladkrabang Industrial Estate
Ladkrabang ICD Depot 
Takiab Beach, Prachub Kirikhan
Pranburi Dam, Prachub Kirikhan
Chumphon Railway Depot
Huahin Railway Station
Ramkamhang University
Vientian, LAO PDR
Mae Sai, chiang rai



Primary Key:
the primary key is an Int per RDBS.
the location ID column is unique and is seeded from ECB file. Length is 15-char
AAA-AAAA-AAA-AA  This code book is maintained via Google Sheets

Each AOI has:
1. id
2. loc_uid
3. loc_code - for correlating with SmoothStreets version 1.
4. utm_coord
5. lat
6. long
7. polygon_id
8. map_projection
9. map_utm_zone
10. title
11. name
12. description
13. updated_at
14. created_by
15. area_sqkm
16. poi_count


Map Editor form:
- TkInter app
MapEditor(App)

1. SyncAOI(MapEditor)
2. EditAOI(MapEditor)
3. ViewAOI(MapEditor)
4. ImportAOI
5. ExportAOI



