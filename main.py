from fastapi import FastAPI
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MultiLabelBinarizer
from ast import literal_eval
df_EDA= pd.read_csv('df_EDA.csv')
df= pd.read_csv('data.csv')
app= FastAPI()

def convert_to_list(x):
        try:
            return literal_eval(x)
        except (ValueError, SyntaxError):
            return [] 
        
def filtrar_por_año(Año):
    Año_str = str(Año)  # Convertir el año a una cadena (str)
    return df[df['release_date'].str.contains(Año_str, na=False)]

# Endpoint: /genero/
@app.get('/genero/')
def genero(Año: str):
    df_filtrado = filtrar_por_año(Año) 
    df_filtrado['genres'] = df_filtrado['genres'].apply(convert_to_list)    
    df_filtrado['genres'] = df_filtrado['genres'].apply(lambda x: x if x != 0 else '')
    genero_contado={}
    for i in df_filtrado['genres']:
        for j in i :
            genero_contado[j]= genero_contado.get(j,0)+1

    generos_mas_vendidos = sorted(genero_contado , key=genero_contado.get, reverse=True)[:5] # Ordenar de mayor a menor y tomar los 3 primeros
    generos_mas_vendidos_dict = {genero: genero_contado[genero] for genero in generos_mas_vendidos}
    return generos_mas_vendidos_dict
# Endpoint: /juegos/
@app.get('/juegos/')
def juegos(Año: str):
    df_filtrado= filtrar_por_año(Año)
    df_filtrado['app_name'] = df_filtrado['app_name'].apply(lambda x: x if x != 0 else '')
    lista_juegos=[]
    for name in df_filtrado['app_name']:
        lista_juegos.append(name)
    return lista_juegos    

# Endpoint: /specs/

@app.get('/specs/')
def specs(Año: str):
    df_filtrado = filtrar_por_año(Año)
    df_filtrado['specs'] = df_filtrado['specs'].apply(convert_to_list)
    df_filtrado['specs'] = df_filtrado['specs'].apply(lambda x: x if x != 0 else '')
    
    specs_contados = {}
    for i in df_filtrado['specs']:
        for j in i:
            specs_contados[j] = specs_contados.get(j, 0) + 1

    specs_mas_repetidos = {spec: specs_contados[spec] for spec in sorted(specs_contados, key=specs_contados.get, reverse=True)[:5]}

    return specs_mas_repetidos        


# Endpoint: /early_access/
@app.get('/early_access/')
def early_access(Año: str):
    df_filtrado= filtrar_por_año(Año)
    cantidad_ea= len(df_filtrado['early_access'])
    return cantidad_ea

# Endpoint: /sentiment/
@app.get('/sentiment/')
def sentiment(Año: str):
    df_filtrado= filtrar_por_año(Año)
    df_filtrado['sentiment']= df_filtrado['sentiment'].apply(lambda x: x if x != 0 else '')
    df_filtrado =df_filtrado[~df_filtrado['sentiment'].str.contains(' user reviews',case=False, na=False) ]
    sentimientos_contados= df_filtrado['sentiment'].value_counts().to_dict()
    return sentimientos_contados

# Endpoint: /metascore/
@app.get('/metascore/')
def metascore(Año: str):
    df_filtrado = filtrar_por_año(Año)
    df_filtrado_ordenado = df_filtrado.sort_values(by='metascore', ascending=False)
    top_5 = df_filtrado_ordenado.head(5)
    
    result_dict = {
        'top_5_app_names': top_5['app_name'].tolist(),
        'top_5_metascores': top_5['metascore'].tolist()
    }
    
    return result_dict


# ML
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(df_EDA['valor'])
y = df_EDA['price']

modelo_precio = LinearRegression()
modelo_precio.fit(X, y)

# Función de predicción
@app.get('/prediccion/')
def prediccion(genero):
    genero_encoded_input = mlb.transform([[genero]])
    precio_predicho = modelo_precio.predict(genero_encoded_input)
    return precio_predicho


#if __name__ == "__main__":
    # Ejemplo de uso de la función prediccion
 #   genero_input = 'Action, Casual, Indie, Simulation, Strategy'
  #  precio_estimado = prediccion(genero_input)
   # print(f'Precio estimado para el género "{genero_input}": {precio_estimado}')