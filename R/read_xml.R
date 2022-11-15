library(jsonlite)
library(lubridate)

df_c = read.csv('/home/oscar/Escritorio/skywood-urban-example/track_points.csv', header=FALSE)
df_c = df_c[, c("V1", "V2", "V7")]

df_co = fromJSON("/home/oscar/Escritorio/response_1668468360413.json")    

df_c$V7 = ymd_hms(df_c$V7)
df_co$DATE_C = ymd_hm(df_co$DATE_C)


df = df_co[df_co$ORIGIN == "Sensor1",]
df = df_co[df_co$CO2 >= 200 & df_co$CO2 <= 500 ,]

df = df[1:158,]
df_c$CO = df$CO2

colnames(df_c) = c("LAT", "LON", "DATE", "CO2")

write.csv(df_c, "/home/oscar/Escritorio/map.csv")
