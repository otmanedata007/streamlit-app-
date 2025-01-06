import streamlit as st
from utils.data_loader import load_data
from utils.knn_recommendations import knn_recommendations
from utils.language_utils import get_synopsis_in_language, render_language_selector
from utils.display_utils import display_movie_with_synopsis, clean_actor_list
from utils.style_utils import set_background
from datetime import datetime

# Configurer la mise en page
st.set_page_config(layout="wide")

# Ajouter un fond d'écran
image_path = "assets/cinema.old.webp"
set_background(image_path)

# Charger les données
csv_path = "assets/df_movie_tmdb_1.csv"  # Remplacez par le chemin correct
df = load_data(csv_path)

# Initialiser la langue par défaut si elle n'est pas déjà définie
if "language" not in st.session_state:
    st.session_state.language = "fr"  # Valeur par défaut

# Initialiser le menu par défaut si elle n'est pas déjà définie
if "menu" not in st.session_state:
    st.session_state.menu = "Page d'accueil"  # Valeur par défaut

# Barre de menu en haut
st.markdown("""
    <style>
        .menu-bar {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .menu-bar button {
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            border: none;
            background-color: #4CAF50;
            color: black !important;  /* Forcer la couleur du texte en noir */
            cursor: pointer;
        }
        .menu-bar button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# Créer une ligne de boutons centrés pour le menu
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Page d'accueil", key="home"):
        st.session_state.menu = "Page d'accueil"
with col2:
    if st.button("Recherche par films", key="search_movies"):
        st.session_state.menu = "Recherche par films"
with col3:
    if st.button("Films par acteur", key="movies_by_actor"):
        st.session_state.menu = "Films par acteur"
with col4:
    if st.button("Recherche par genre", key="search_by_genre"):
        st.session_state.menu = "Recherche par genre"

# Ajouter le filtre d'année dans le menu de gauche
with st.sidebar:
    st.write("### Filtre par année")
    start_year, end_year = st.slider("Sélectionner la période", 1900, 2024, (1900, 2024), step=1)

# Page d'accueil
if st.session_state.menu == "Page d'accueil":
    st.markdown("<h1 style='font-size: 40px;'>🎥 Bienvenue au cinéma de la CREUSE</h1>", unsafe_allow_html=True)
    render_language_selector()  # Afficher le sélecteur de langue dans le menu de gauche

    # Barre latérale pour les filtres
    with st.sidebar:
        st.write("### Trier par")
        sort_option = st.radio("Options de tri", ["Aucun tri", "Année de sortie (croissant)", "Année de sortie (décroissant)", "Note (meilleure à moins bonne)"])

    genres_list = ['Comedy', 'Documentary', 'Action', 'Animation', 'Family']  # Liste des genres

    current_year = datetime.now().year
    recent_movies = df[(df['URL_AFFICHE'].notnull())]

    for genre in genres_list:
        st.markdown(f"### Films dans le genre : {genre}")
        genre_movies = recent_movies[recent_movies['Genres'].str.contains(genre, na=False)]

        # Appliquer le filtre d'année
        genre_movies = genre_movies[(genre_movies['Year'] >= start_year) & (genre_movies['Year'] <= end_year)]

        # Appliquer le tri uniquement si l'utilisateur choisit une option de tri
        if sort_option == "Année de sortie (croissant)":
            genre_movies = genre_movies.sort_values(by='Year', ascending=True)
        elif sort_option == "Année de sortie (décroissant)":
            genre_movies = genre_movies.sort_values(by='Year', ascending=False)
        elif sort_option == "Note (meilleure à moins bonne)":
            genre_movies['Rating'] = pd.to_numeric(genre_movies['Vote_average'], errors='coerce')
            genre_movies = genre_movies.sort_values(by='Rating', ascending=False)

        if not genre_movies.empty:
            # Afficher 5 films par ligne
            cols = st.columns(5)  # Créer 5 colonnes
            for i, (_, row) in enumerate(genre_movies.iterrows()):
                if i >= 5:  # Limiter à 5 films par ligne
                    break
                with cols[i % 5]:
                    translated_synopsis = get_synopsis_in_language(row['Description'], st.session_state.language)
                    display_movie_with_synopsis(row, translated_synopsis)

# Page Recherche par film
elif st.session_state.menu == "Recherche par films":
    st.markdown("<h1 style='font-size: 40px;'>🔍 Recherche par film</h1>", unsafe_allow_html=True)
    render_language_selector()  # Afficher le sélecteur de langue dans le menu de gauche

    # Barre latérale pour les filtres
    with st.sidebar:
        st.write("### Trier par")
        sort_option = st.radio(
            "Options de tri", ["Aucun tri", "Année de sortie (croissant)", "Année de sortie (décroissant)", "Note (meilleure à moins bonne)"], key="movie_sort_option"
        )

    # Liste des titres de films
    movie_list = df['Title'].str.strip().unique().tolist()  # Liste des titres uniques
    movie_list = [movie.title() for movie in movie_list]  # Formater les titres (optionnel)

    # Barre de recherche avec suggestions (centrée et réduite)
    col1, col2, col3 = st.columns([1, 2, 1])  # Créer 3 colonnes (la colonne du milieu est plus large)
    with col2:  # Utiliser la colonne du milieu pour centrer la barre de recherche
        movie_search = st.selectbox("Recherche un film :", ["Tout"] + movie_list, key="movie_search")

    # Si "Tout" est sélectionné, ne rien afficher
    if movie_search == "Tout":
        st.write("Veuillez sélectionner un film pour afficher les résultats.")
    else:
        # Recherche par titre exact
        movie_results = df[df['Title'].str.strip().str.lower() == movie_search.strip().lower()]

        # Appliquer le filtre d'année
        movie_results = movie_results[(movie_results['Year'] >= start_year) & (movie_results['Year'] <= end_year)]

        # Appliquer le tri uniquement si l'utilisateur choisit une option de tri
        if sort_option == "Année de sortie (croissant)":
            movie_results = movie_results.sort_values(by='Year', ascending=True)
        elif sort_option == "Année de sortie (décroissant)":
            movie_results = movie_results.sort_values(by='Year', ascending=False)
        elif sort_option == "Note (meilleure à moins bonne)":
            movie_results['Rating'] = pd.to_numeric(movie_results['Vote_average'], errors='coerce')
            movie_results = movie_results.sort_values(by='Rating', ascending=False)

        # Afficher les résultats de la recherche
        if not movie_results.empty:
            st.markdown(f"### Résultats pour '{movie_search}'")
            cols = st.columns(5)  # 5 films par ligne
            for i, (_, row) in enumerate(movie_results.iterrows()):
                with cols[i % 5]:
                    translated_synopsis = get_synopsis_in_language(row['Description'], st.session_state.language)
                    display_movie_with_synopsis(row, translated_synopsis)
        else:
            st.write("Aucun résultat trouvé pour votre recherche.")

        # Recommandation KNN (uniquement si un film spécifique est sélectionné)
        st.markdown(f"### Suggestions basées sur '{movie_search}'")
        knn_results = knn_recommendations(movie_search, df, k=10)
        knn_results = knn_results[(knn_results['Year'] >= start_year) & (knn_results['Year'] <= end_year)]

        if not knn_results.empty:
            cols = st.columns(5)  # 5 films par ligne
            for i, (_, row) in enumerate(knn_results.iterrows()):
                with cols[i % 5]:
                    translated_synopsis = get_synopsis_in_language(row['Description'], st.session_state.language)
                    display_movie_with_synopsis(row, translated_synopsis)
        else:
            st.write("Aucune suggestion disponible pour ce film.")

# Page Films par acteur
elif st.session_state.menu == "Films par acteur":
    st.markdown("<h1 style='font-size: 40px;'>🎭 Films par acteur</h1>", unsafe_allow_html=True)
    render_language_selector()  # Afficher le sélecteur de langue dans le menu de gauche

    # Barre latérale pour les filtres
    with st.sidebar:
        st.write("### Trier par")
        sort_option = st.radio(
            "Options de tri", ["Aucun tri", "Année de sortie (croissant)", "Année de sortie (décroissant)", "Note (meilleure à moins bonne)"], key="actor_sort_option"
        )

    # Liste des acteurs
    actor_list = df['All_Actors'].str.split(', ').explode().dropna().unique().tolist()
    actor_list = [clean_actor_list(actor) for actor in actor_list]  # Nettoyer les acteurs
    actor_filter = st.selectbox("Choisissez un acteur :", ["Tous"] + actor_list, key="actor_selectbox")

    if actor_filter != "Tous":
        actor_movies = df[df['All_Actors'].str.contains(actor_filter, na=False, regex=False)]
        # Appliquer le filtre d'année
        actor_movies = actor_movies[(actor_movies['Year'] >= start_year) & (actor_movies['Year'] <= end_year)]

        # Appliquer le tri uniquement si l'utilisateur choisit une option de tri
        if sort_option == "Année de sortie (croissant)":
            actor_movies = actor_movies.sort_values(by='Year', ascending=True)
        elif sort_option == "Année de sortie (décroissant)":
            actor_movies = actor_movies.sort_values(by='Year', ascending=False)
        elif sort_option == "Note (meilleure à moins bonne)":
            actor_movies['Rating'] = pd.to_numeric(actor_movies['Vote_average'], errors='coerce')
            actor_movies = actor_movies.sort_values(by='Rating', ascending=False)

        if not actor_movies.empty:
            st.markdown(f"### Films avec {actor_filter}")
            cols = st.columns(5)  # 5 films par ligne
            for i, (_, row) in enumerate(actor_movies.iterrows()):
                with cols[i % 5]:
                    translated_synopsis = get_synopsis_in_language(row['Description'], st.session_state.language)
                    display_movie_with_synopsis(row, translated_synopsis)
    else:
        st.write("Veuillez sélectionner un acteur pour afficher les films.")

# Page Recherche par genre
elif st.session_state.menu == "Recherche par genre":
    st.markdown("<h1 style='font-size: 40px;'>🎬 Films par genre</h1>", unsafe_allow_html=True)
    render_language_selector()  # Afficher le sélecteur de langue dans le menu de gauche

    # Barre latérale pour les filtres
    with st.sidebar:
        st.write("### Trier par")
        sort_option = st.radio(
            "Options de tri", ["Aucun tri", "Année de sortie (croissant)", "Année de sortie (décroissant)", "Note (meilleure à moins bonne)"], key="genre_sort_option"
        )

    genres_list = ['Tout', 'Comedy', 'Documentary', 'Action', 'Animation', 'Family']  # Liste des genres
    genre_filter = st.selectbox("Choisissez un genre :", genres_list, key="genre_selectbox")

    if genre_filter != "Tout":
        genre_movies = df[df['Genres'].str.contains(genre_filter, na=False)]
        # Appliquer le filtre d'année
        genre_movies = genre_movies[(genre_movies['Year'] >= start_year) & (genre_movies['Year'] <= end_year)]

        # Appliquer le tri uniquement si l'utilisateur choisit une option de tri
        if sort_option == "Année de sortie (croissant)":
            genre_movies = genre_movies.sort_values(by='Year', ascending=True)
        elif sort_option == "Année de sortie (décroissant)":
            genre_movies = genre_movies.sort_values(by='Year', ascending=False)
        elif sort_option == "Note (meilleure à moins bonne)":
            genre_movies['Rating'] = pd.to_numeric(genre_movies['Vote_average'], errors='coerce')
            genre_movies = genre_movies.sort_values(by='Rating', ascending=False)

        if not genre_movies.empty:
            st.markdown(f"### Films dans le genre : {genre_filter}")
            cols = st.columns(5)  # 5 films par ligne
            for i, (_, row) in enumerate(genre_movies.iterrows()):
                with cols[i % 5]:
                    translated_synopsis = get_synopsis_in_language(row['Description'], st.session_state.language)
                    display_movie_with_synopsis(row, translated_synopsis)
    else:
        st.write("Veuillez sélectionner un genre pour afficher les films.")
