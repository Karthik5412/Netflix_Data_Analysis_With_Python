import streamlit as st 
import plotly.express as px
import pandas as pd
import joblib
import numpy as np

unique_actors = joblib.load('unique_actors.plk') 

df = pd.read_csv('cleaned.csv')

df['date_added'] = pd.to_datetime(df['date_added'])


st.title('LETTERBOXD MOVIES ANALYSIS FROM 2K10 TO 2k25')
st.set_page_config(page_title='Movie Data Analysis',layout='wide',initial_sidebar_state='collapsed')

letterboxd_palette = [
    "#FF8000", "#00E054", "#40BCF4", "#9129FF", "#FF4500", 
    "#00B0F0", "#2ECC71", "#E74C3C", "#F1C40F", "#9B59B6",
    "#1ABC9C", "#E67E22", "#3498DB", "#FF005A", "#00FA9A",
    "#8E44AD", "#C0392B", "#16A085", "#D35400", "#2980B9"
]


    

countries = st.sidebar.multiselect(
    'Select the country',
    options=df['country'].unique()
)

director = st.sidebar.multiselect(
    'Select Director',
    options=df['director'].unique()
)

actors = st.sidebar.multiselect(
    'Select Actors',
    options=unique_actors,
)

gener = st.sidebar.multiselect(
    'Select Gener',
    options=df['genres'].unique()
)

start_year = st.sidebar.date_input('Select Year Start Year',min_value=df['date_added'].min(),max_value=df['date_added'].max(),)
end_year = st.sidebar.date_input('Select Year End Year',min_value=df['date_added'].min(),max_value=df['date_added'].max())

if countries or director  or actors:
    condition = 'country in @countries or director in @director or genres in @gener'
    df = df.query(
        condition
    )

le_col,cen_col,rt_col = st.columns(3)

with le_col :
    
    st.subheader('Avg Budget')
    new_df = df.drop_duplicates(subset='title')
    st.header(f'$ {new_df['budget'].mean():.2f}')
    
with cen_col :
    
    st.subheader('Avg Revenue')
    new_df = df.drop_duplicates(subset='title')
    st.header(f'$ {new_df['revenue'].mean():.2f}')
with rt_col :
    st.subheader('Profit Percentage')
    new_df = df.drop_duplicates(subset='title')
    num = (new_df['revenue'] - new_df['budget']).sum()
    den = new_df['budget'].sum()
    st.header(f'{(num / den) * 100:.2f} % ')

tab1,tab2,tab3 = st.tabs(['Revenue','Popularity','Rating'])

with tab1 :
    col1, col2 = st.columns(2)
    with col1:
        
        new_df = df.groupby('country')['revenue'].mean().reset_index()
        fig = px.choropleth(new_df,locations='country',
                            locationmode='country names',
                            color='revenue',
                            hover_data=['country','revenue'],
                            color_continuous_scale=letterboxd_palette)
        
        st.plotly_chart(fig,key='revenue map')
        
    with col2: 
        fig_scatter = px.scatter(df,x='budget',y='revenue',
                                hover_data=['title','budget','revenue'],
                                color_discrete_sequence= letterboxd_palette)
        st.plotly_chart(fig_scatter) 

        
    new_df = df.groupby('date_added')[['revenue','budget']].sum().reset_index()
    new_df = new_df.sort_values(by='date_added',ascending=True)
        
    fig = px.line(new_df, x = 'date_added', 
                            y= ['revenue','budget'],
                            color_discrete_sequence=letterboxd_palette,
                            line_shape= 'linear',
                    )
        
    st.plotly_chart(fig)


    col4,col5 = st.columns(2)  

    with col4:
        new_df = df.nlargest(20,'revenue').reset_index()
        
        fig = px.bar(new_df,y='title',x=['revenue','budget'],orientation='h',
                    color_discrete_sequence=letterboxd_palette)
        st.plotly_chart(fig)
    
    with col5: 
        
        fig = px.pie(df,names='genres',values='revenue',hole=0.7,
                    color_discrete_sequence=letterboxd_palette)
        st.plotly_chart(fig)
        
        
with tab2:    
        col1,col2 = st.columns(2)
        
        with col1:
            new_df = df.groupby('date_added')['popularity'].mean().reset_index()
            
            fig = px.area(new_df,x = 'date_added',y = 'popularity')
            st.plotly_chart(fig)
            
        with col2 :
            new_df = df.groupby('genres')['popularity'].mean().reset_index()
            new_df = new_df.nlargest(10,'popularity').reset_index()
            
            fig = px.pie(new_df,names='genres',values='popularity',hole=0.7,color_discrete_sequence=letterboxd_palette)
            
            st.plotly_chart(fig)
            
        new_df = df['date_added'].value_counts().reset_index()
        new_df = new_df.sort_values(by='date_added').reset_index()
        
        fig = px.bar(new_df,x='date_added',y='count',color_discrete_sequence=letterboxd_palette[6:])
        st.plotly_chart(fig)
        
        col4,col5 = st.columns([5,5])
        
        with col4 :
            
            fig = px.histogram(df,x='rating', y= 'popularity', nbins=100, color_discrete_sequence=letterboxd_palette[3:])
            st.plotly_chart(fig)
            
        with col5 :
            
            gener_df_year = df.copy()
            gener_df_year['date_added'] = pd.to_datetime(gener_df_year['date_added']).dt.strftime('%Y')
            new_df = df.groupby(['date_added','genres'])['popularity'].mean().reset_index()
             
            fig = px.scatter(new_df,x='date_added',y='popularity',
                             color='genres',size='popularity',
                             color_discrete_sequence=letterboxd_palette)
            
            st.plotly_chart(fig)
            
with tab3:
    
    col1,col2 = st.columns(2)
    
    with col1 :
        new_df = df.groupby('genres')[['rating','popularity']].mean().reset_index()
        fig = px.scatter(new_df,x='rating',y='popularity',
                        hover_name='genres',
                        size = 'popularity',color='genres',
                        marginal_x="box",marginal_y='box',
                        color_discrete_sequence=letterboxd_palette)

        st.plotly_chart(fig,use_container_width=True,width='constent',height='stretch')
        
    with col2:
        new_df = df.groupby('date_added')['rating'].mean().reset_index()
        
        
        fig = px.histogram(new_df,x='date_added',y='rating',histfunc='avg',
                     marginal='violin',nbins=50,
                     color_discrete_sequence=letterboxd_palette)
        
        st.plotly_chart(fig,use_container_width=True,width='constent',height='stretch')
        
    new_df = df.groupby('genres').agg({
        'rating' : 'mean',
        'revenue' : 'sum'
    }).reset_index()
    
    fig = px.treemap(
    new_df,
    path=[px.Constant("All Genres"), 'genres'],
    values='revenue', color='rating',
    color_continuous_scale=letterboxd_palette)
    
    st.plotly_chart(fig,use_container_width=True,width='constent',height='stretch')
        
    
    new_df = df.groupby(['genres','date_added'])['rating'].mean().reset_index()
    new_df['date_added'] = pd.to_datetime(new_df['date_added']).dt.strftime('%Y-%Q%q')
    new_df = new_df.sort_values(by='date_added',ascending=True)
    
    fig = px.line(new_df,x='date_added',y='rating',color='genres',color_discrete_sequence=letterboxd_palette)

    st.plotly_chart(fig,use_container_width=True,width='constent',height='stretch')
    
    
    new_df = df.groupby('country')['rating'].mean().reset_index()
    fig = px.bar(new_df.nlargest(100,'rating') ,x='country',y='rating',
                    barmode='stack',
                    color_discrete_sequence=letterboxd_palette[3:])
    st.plotly_chart(fig,use_container_width=True,width='constent',height='stretch')
    
        
    

    
            
            
            
            
            



