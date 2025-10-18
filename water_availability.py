import geopandas as gpd
import folium
from flask import Flask
from flask import render_template, request

# Initialize Flask app
app = Flask(__name__)

# Load geospatial data
gdf = gpd.read_file('./static/ast_ketersediaan_air.geojson')
nama_wd_list = gdf['nama_wd'].dropna().unique().tolist()
nama_ws_list = gdf['nama_ws'].dropna().unique().tolist()
kls_ktrs_list = gdf['kls_ktrs'].dropna().unique().tolist()
kls_nrcair_list = gdf['kls_nrcair'].dropna().unique().tolist()
kls_ipa_list = gdf['kls_ipa'].dropna().unique().tolist()


@app.route('/', methods=['GET','POST'])
def index():
    nama_wd = ''
    nama_ws = ''
    kls_ktrs = ''
    kls_nrcair = ''
    kls_ipa = ''
    is_gdf_empty = False

    # Create a Folium map centered on the data
    m  = folium.Map(location=[-6.5, 106.5], zoom_start=5)

    filtered_gdf = gdf

    # Handle form submission
    if request.method == 'POST':
        nama_wd = request.form.get('nama_wd','')
        nama_ws = request.form.get('nama_ws','')
        kls_ktrs = request.form.get('kls_ktrs','')
        kls_nrcair = request.form.get('kls_nrcair','')
        kls_ipa = request.form.get('kls_ipa','')

        # Apply filters based on form inputs
        filtered_gdf = gdf[
            (gdf['nama_wd'].str.contains(nama_wd, case=False, na=False)) &
            (gdf['nama_ws'].str.contains(nama_ws, case=False, na=False)) &
            (gdf['kls_ktrs'].str.contains(kls_ktrs, case=False, na=False)) &
            (gdf['kls_nrcair'].str.contains(kls_nrcair, case=False, na=False)) &
            (gdf['kls_ipa'].str.contains(kls_ipa, case=False, na=False))
            ]   
        
    # Add filtered GeoJSON layer to the map
    if not filtered_gdf.empty:
        folium.GeoJson(
            filtered_gdf,
            name='Water Availability Polygons',
            tooltip=folium.GeoJsonTooltip(
                fields=['nama_wd','nama_ws','ktrs_air','kbth_air','kls_ktrs','kls_nrcair','kls_ipa', 'populasi', 'status'],
                aliases=['Water District Name:', 'Watershed Name:','Water Availability:', 'Water Demand:','Water Availability Class:','Water Balance Class:','Water Quality Class:','Population:','Status:'],
                localize=True
            ),
            style_function=lambda feature:{
                'fillColor': 
                'green' if feature['properties']['kls_ktrs'] == 'Tanpa Tekanan' else 'orange' if feature['properties']['kls_ktrs'] == 'Ada Tekanan' else 'red' if feature['properties']['kls_ktrs'] == 'Ada Kelangkaan' else 'darkred',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5,
            }
        ).add_to(m)
    else:
        # If no data matches the filters, do not add any layer
        is_gdf_empty = True
        pass


    # Add layer control to the map
    folium.LayerControl().add_to(m)

    # Save map to HTML file
    map_html = m._repr_html_()
    return render_template('index.html', map_html=map_html, kls_ipa=kls_ipa, nama_wd=nama_wd, nama_ws=nama_ws, kls_ktrs=kls_ktrs, kls_nrcair=kls_nrcair, selected_region=nama_wd, selected_river=nama_ws, selected_availability=kls_ktrs, selected_balance=kls_nrcair, selected_quality=kls_ipa, nama_wd_list=nama_wd_list, nama_ws_list=nama_ws_list, kls_ktrs_list=kls_ktrs_list, kls_nrcair_list=kls_nrcair_list, kls_ipa_list=kls_ipa_list, is_gdf_empty=is_gdf_empty)

if __name__ == '__main__':
    app.run(debug=True)