import streamlit as st



st.set_page_config(page_title="Accessibility web app", 
                   page_icon="🌍", 
                   layout="wide", 
                   initial_sidebar_state="auto")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)
st.markdown("""
<style>
@media (max-width: 600px) {
  .author-container {
    flex-direction: column;
  }
  .author {
    margin-right: 0;
    margin-bottom: 20px;
  }
}
</style>
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Measuring equity of access in Finland with open-source GIS-tools</h2>
   <img style="margin-left: 20px; margin-bottom: 8px;" src="https://raw.githubusercontent.com/ipeaGIT/r5r/master/r-package/man/figures/r5r_blue.png" width="100" height="110">
 </div>
 <span style="font-size: 18px;">This app was developed to showcase some of the capabilities of open-source GIS-tools and the national datasets produced for the research paper <i>Measuring equity of access in Finland with open-source GIS-tools</i>. With the app you can analyze the disparity and sufficiency of accessibility in a national context and explore the distribution of different opportunities and services that most people consider necessities in their daily lives. You have also the possibility to compare access differences between Finnish municipalities and investigate the number of opportunities accessible by public transport or bicycle within certain travel time thresholds. Additionally, you have the possibility to use this tool to analyze the equity of access differences between municipalities.</span>
<br><br>
<h4 style="margin-left: -10px;">👈 From the sidebar you can start to explore different datasets produced for the research paper.</h4>
<br><br><br>
<div style="text-align: center; margin-right: 80px">
  <h4><i>Page authors</i><br></h4>
</div>
<br>
<div class="author-container" style="display: flex; align-items: center; justify-content: center;">
   <div class="author" style="display: flex; flex-direction: column; align-items: center; margin-right: 80px;">
     <img src="https://www.flou.io/img/ner_5277.jpg" style="border-radius: 50%; width: 150px; height: 150px;">
     <span style="margin-top: 15px;"><b>Matti Pönkänen</b>
            <br>FLOU ltd <a href="https://www.linkedin.com/in/matti-p%C3%B6nk%C3%A4nen-476040174/" target="_blank"><i class="fas fa-link" style="font-size: 18px; margin-top: 2px; color: lightgrey"></i></a> 
     </span>
   </div>
   <div class="author" style="display: flex; flex-direction: column; align-items: center; margin-right: 80px;">
     <img src="https://people.aalto.fi/files/1213981_x_512_3to4.jpg" style="border-radius: 50%; width: 150px; height: 150px; object-fit: cover; object-position: 50% 35%;">
     <span style="margin-top: 15px;"><b>Henrikki Tenkanen</b>
            <br>Aalto University <a href="https://research.aalto.fi/fi/persons/henrikki-tenkanen" target="_blank"><i class="fas fa-link" style="font-size: 18px; margin-top: 2px; color: lightgrey"></i></a> 
     </span>
   </div>
   <div div class="author" style="display: flex; flex-direction: column; align-items:center; margin-right: 80px">
     <img src="https://media.licdn.com/dms/image/D4D03AQGxOHqmGuOjJw/profile-displayphoto-shrink_400_400/0/1683380472067?e=1699488000&v=beta&t=YE6pMorFf3PaF_5XEhofVikjyFSBkUalUPVGTBjjMg8" style="border-radius:50%; width: 150px; height: 150px; object-fit: cover;">
     <span style="margin-top: 15px;"><b>Miloš Mladenović</b>
            <br>Aalto University <a href="https://research.aalto.fi/en/persons/milos-mladenovic" target="_blank"><i class="fas fa-link" style="font-size: 18px; margin-top: 2px; color: lightgrey"></i></a> 
     </span>
   </div>
 </div>

 <br><br>
 <div style="text-align: center; margin-right: 80px">
  <i>Service hosted by GIST Lab, Aalto University. Licensed under CC-BY.</i>
  <br><br>
  <img style="margin-right: 0px; margin-bottom: 8px;" src="https://gistlab.science/wp-content/uploads/2023/08/Aalto_logo_black.png" width="300">
 </div>

 """, unsafe_allow_html=True)
 