library(ggmap)
library(ggplot2)

data = read.csv("/home/oscar/Escritorio/map.csv", dec=",")
# data$LAT =  sub(".", ",", data$LAT, fixed = TRUE)
data$LAT =  as.double(data$LAT)

# data$LON =  sub(".", ",", data$LON, fixed = TRUE)
data$LON=  as.double(data$LON)

register_google(key = "AIzaSyD1X3sw4Lw0WDLXZDzSdYYkxDanvlVgvv0") #AIzaSyArt2RgDClSbg4g3ngF7wCD6DA7nnCs-l0

data_map = get_map(location = c(-74.0648854, 4.7565838), # la función get_map me permite tomar el mapa
                  zoom = 16, # nivel de zoom
                  maptype = "hybrid"
                  )

gg = ggmap(data_map,# ingre4o el mapa
            extent = "device" # para que el mapa se extienda donde se encuentre
            ) +
        geom_density2d(data = data, 
                       aes(x = LAT, y = LON), # coordenadas de los puntos
                       size = 0.3 # tamaño de los puntos
          ) +
        stat_density2d(data = data,
                       aes(x = LAT, y = LON,
                           fill = ..level.., # con ..fill.. entre mas concentrados esten los puntos
                           alpha = ..level..), # coordenadas de los puntos
                       size = 1, # tamaño de los puntos
                       bins = 30, # número de divsiones
                       geom = "polygon" # geometría poligonos
        ) +
        scale_fill_gradient(low = "green", high = "red",
                            guide = "colourbar",
                            labels = NULL,
                            name = "Mapa") + # fijo un gradiente de color
        scale_alpha(range = c(0, 0.25), # establezco el rango de la transparencia
                    guide = FALSE # quito la leyenda de los datos
                    ) +
        labs(title = "Mapa")
gg 

