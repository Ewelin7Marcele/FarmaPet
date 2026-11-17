"""FarmaPet — protótipo acadêmico de apoio à farmacologia veterinária.
Não prescreve doses nem substitui avaliação médico-veterinária.
"""
from __future__ import annotations
from datetime import datetime
from io import BytesIO
import html
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from farmacologia import calcular_quantidade
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

st.set_page_config(page_title="FarmaPet | Farmacologia veterinária", page_icon="🐾", layout="wide")

# Callbacks devem ser definidos antes de qualquer botão que os utilize.
def go_to_dashboard():
    st.session_state["nav_page"] = "Dashboard"

def go_to_home():
    st.session_state["nav_page"] = "Início"

def go_to_about():
    st.session_state["nav_page"] = "Sobre e referências"

GREEN = "#426b50"
REFERENCES = [
    {"title":"Intoxicação de animais por medicamentos humanos sem prescrição", "source":"Manual MSD de veterinária", "category":"Toxicologia", "url":"https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%A3o-por-medicamentos-humanos-de-venda-livre"},
    {"title":"Intoxicações por medicamentos humanos sob prescrição", "source":"Manual MSD de veterinária", "category":"Toxicologia", "url":"https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%B5es-por-medicamentos-humanos-de-prescri%C3%A7%C3%A3o-m%C3%A9dica"},
    {"title":"Intoxicação de cães e gatos por medicamentos de uso humano", "source":"The Veterinary Journal, 2015; PubMed", "category":"Toxicologia", "url":"https://pubmed.ncbi.nlm.nih.gov/25475169/"},
    {"title":"Substâncias tóxicas para cães e gatos", "source":"Cornell University College of Veterinary Medicine", "category":"Toxicologia", "url":"https://www.vet.cornell.edu/hospitals/pharmacy/consumer-clinical-care-guidelines-animals/small-animal-toxins"},
    {"title":"Consenso ACVIM: uso racional de protetores gastrointestinais em cães e gatos", "source":"Journal of Veterinary Internal Medicine, 2018", "category":"Farmacologia", "url":"https://onlinelibrary.wiley.com/doi/10.1111/jvim.15337"},
    {"title":"Uso racional de protetores gastrointestinais em gatos", "source":"Journal of Feline Medicine and Surgery, 2024", "category":"Farmacologia", "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11418625/"},
    {"title":"Princípios do tratamento de intoxicações em animais", "source":"Manual MSD de veterinária", "category":"Toxicologia", "url":"https://www.msdvetmanual.com/pt/toxicology/introdu%C3%A7%C3%A3o-%C3%A0-toxicologia/princ%C3%ADpios-do-tratamento-das-toxicoses-em-animais"},
    {"title":"Diretrizes WSAVA 2022 para reconhecimento, avaliação e tratamento da dor", "source":"WSAVA, versão em português", "category":"Farmacologia", "url":"https://wsava.org/wp-content/uploads/2023/08/Portugues_2022-WSAVA-Diretrizes-de-dor.pdf"},
    {"title":"Consenso ISFM/AAFP 2024 sobre uso prolongado de AINEs em gatos", "source":"Journal of Feline Medicine and Surgery, 2024", "category":"Farmacologia", "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11103309/"},
    {"title":"Disposição e destino dos medicamentos: farmacocinética", "source":"Manual MSD de veterinária", "category":"Farmacocinética", "url":"https://www.msdvetmanual.com/pt/pharmacology/introdu%C3%A7%C3%A3o-%C3%A0-farmacologia/disposi%C3%A7%C3%A3o-e-destino-dos-medicamentos"},
    {"title":"Ação dos medicamentos em animais: farmacodinâmica", "source":"Manual MSD de veterinária", "category":"Farmacodinâmica", "url":"https://www.msdvetmanual.com/pt/pharmacology/introdu%C3%A7%C3%A3o-%C3%A0-farmacologia/a%C3%A7%C3%A3o-de-medicamentos-em-animais-farmacodin%C3%A2mica"},
    {"title":"Vias de administração e formas farmacêuticas de medicamentos", "source":"Manual MSD de veterinária", "category":"Farmacologia", "url":"https://www.msdvetmanual.com/pt/pharmacology/introdu%C3%A7%C3%A3o-%C3%A0-farmacologia/vias-de-administra%C3%A7%C3%A3o-e-formas-farmac%C3%AAuticas-de-medicamentos"},
    {"title":"Get the Facts about Pain Relievers for Pets", "source":"U.S. Food and Drug Administration", "category":"Segurança", "url":"https://www.fda.gov/animal-veterinary/animal-health-literacy/get-facts-about-pain-relievers-pets"},
]
MEDS = [
 {"name":"Paracetamol (acetaminofeno)","class":"Analgésico e antipirético","species":"Cães: uso veterinário selecionado; gatos: risco elevado e não administrar sem orientação especializada","use":"Há usos veterinários específicos em cães. Gatos são particularmente suscetíveis à toxicidade.","risk":"Pode causar lesão hepática e dano oxidativo às hemácias. Suspeita de ingestão em gato é emergência.","status":"Alto risco sem prescrição","url":"https://www.fda.gov/animal-veterinary/animal-health-literacy/get-facts-about-pain-relievers-pets"},
 {"name":"Ibuprofeno","class":"Anti-inflamatório não esteroidal (AINE)","species":"Cães e gatos: não administrar por conta própria","use":"Não é opção de automedicação veterinária; há alternativas veterinárias com avaliação de risco própria.","risk":"Pode causar ulceração gastrointestinal, hemorragia e lesão renal. Margem de segurança estreita.","status":"Alto risco sem prescrição","url":"https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%A3o-por-medicamentos-humanos-de-venda-livre"},
 {"name":"Naproxeno","class":"Anti-inflamatório não esteroidal (AINE)","species":"Cães e gatos: não administrar por conta própria","use":"Não deve ser usado sem avaliação veterinária.","risk":"Risco de efeitos gastrointestinais graves e lesão renal; ingestão acidental requer atendimento imediato.","status":"Alto risco sem prescrição","url":"https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%B5es-por-medicamentos-humanos-de-prescri%C3%A7%C3%A3o-m%C3%A9dica"},
 {"name":"AAS (ácido acetilsalicílico)","class":"Salicilato; AINE e antiagregante plaquetário","species":"Cães e gatos: diferenças importantes de metabolismo e risco","use":"Há usos veterinários específicos descritos, mas dependem de prescrição e monitoramento.","risk":"Pode causar irritação/ulceração gastrointestinal, alterações de coagulação e intoxicação. Gatos são particularmente suscetíveis.","status":"Exige avaliação veterinária","url":"https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%A3o-por-medicamentos-humanos-de-venda-livre"},
 {"name":"Omeprazol","class":"Inibidor da bomba de prótons","species":"Cães e gatos, conforme indicação","use":"Protetor gastrointestinal em situações clínicas específicas; não é indicado indiscriminadamente.","risk":"Uso desnecessário pode não trazer benefício e pode interferir na absorção de outros fármacos. Avaliar duração e indicação.","status":"Uso sob avaliação veterinária","url":"https://onlinelibrary.wiley.com/doi/10.1111/jvim.15337"},
 {"name":"Famotidina","class":"Antagonista de receptores H₂","species":"Cães e gatos, conforme indicação","use":"Reduz secreção ácida gástrica; evidência e indicação dependem do quadro clínico.","risk":"A eficácia pode diminuir com uso contínuo; ajuste e indicação dependem do paciente.","status":"Uso sob avaliação veterinária","url":"https://www.msdvetmanual.com/pt/pharmacology/farmacoterapia-sist%C3%AAmica-do-sistema-digestivo/medicamentos-usados-para-tratar-%C3%BAlceras-gastrointestinais-em-animais-monog%C3%A1stricos"},
 {"name":"Sucralfato","class":"Protetor de mucosa gastrointestinal","species":"Cães e gatos, conforme indicação","use":"Pode ser utilizado em situações selecionadas de lesão gastrointestinal.","risk":"Pode interferir na absorção de outros medicamentos; intervalo de administração deve ser avaliado pelo profissional.","status":"Uso sob avaliação veterinária","url":"https://www.msdvetmanual.com/pt/pharmacology/farmacoterapia-sist%C3%AAmica-do-sistema-digestivo/medicamentos-usados-para-tratar-%C3%BAlceras-gastrointestinais-em-animais-monog%C3%A1stricos"},
 {"name":"Cetirizina","class":"Anti-histamínico H₁","species":"Cães e gatos: uso e resposta variáveis","use":"Pode ser considerada em situações alérgicas específicas, conforme avaliação veterinária.","risk":"Pode causar sonolência ou efeitos gastrointestinais. Formulações combinadas para humanos podem conter outros ativos perigosos.","status":"Exige avaliação veterinária","url":"https://www.msdvetmanual.com/pt/pharmacology/farmacoterapia-sist%C3%AAmica-do-sistema-tegumentar/anti-histam%C3%ADnicos-para-doen%C3%A7as-tegumentares-em-animais"},
]
INTERACTIONS = [
 ("AINE", "Corticosteroide", "Combinação associada a maior risco de lesões e ulceração gastrointestinal. O uso concomitante ou muito próximo geralmente deve ser evitado, salvo decisão e monitoramento veterinários.", "WSAVA 2022", "https://wsava.org/wp-content/uploads/2023/08/Portugues_2022-WSAVA-Diretrizes-de-dor.pdf"),
 ("AINE", "Outro AINE", "A associação pode aumentar o risco de efeitos gastrointestinais, renais e hepáticos. Não combine nem faça troca sem orientação veterinária.", "Manual MSD", "https://www.msdvetmanual.com/pt/pharmacology/inflama%C3%A7%C3%A3o/medicamentos-anti-inflamat%C3%B3rios-n%C3%A3o-esteroides-em-animais"),
 ("AINE", "Diurético", "Pode aumentar a preocupação com efeitos adversos renais, especialmente em animais desidratados ou com perfusão renal comprometida.", "WSAVA 2022", "https://wsava.org/wp-content/uploads/2023/08/Portugues_2022-WSAVA-Diretrizes-de-dor.pdf"),
 ("AINE", "Inibidor da ECA", "A associação exige cautela: pode alterar a hemodinâmica renal e aumentar o risco de lesão renal em determinados pacientes.", "Manual MSD", "https://www.msdvetmanual.com/pt/pharmacology/farmacoterapia-sist%C3%AAmica-do-sistema-cardiovascular/inibidores-da-enzima-conversora-de-angiotensina-para-uso-em-animais"),
 ("AINE", "Anticoagulante", "A associação exige cautela pelo potencial de aumentar o risco de sangramento. A avaliação depende dos fármacos e do paciente.", "WSAVA 2022", "https://wsava.org/wp-content/uploads/2023/08/Portugues_2022-WSAVA-Diretrizes-de-dor.pdf"),
]
TOXINS = [
 ("Paracetamol", "Não administrar a gatos. Pode causar dano às hemácias e lesão hepática; cães também podem sofrer toxicidade.", "https://www.fda.gov/animal-veterinary/animal-health-literacy/get-facts-about-pain-relievers-pets"),
 ("Ibuprofeno, naproxeno e diclofenaco", "AINEs humanos que podem causar ulceração gastrointestinal, hemorragia e lesão renal. Ingestão acidental é urgência.", "https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%B5es-por-medicamentos-humanos-de-prescri%C3%A7%C3%A3o-m%C3%A9dica"),
 ("Descongestionantes", "Pseudoefedrina e fenilefrina podem provocar alterações cardiovasculares e neurológicas importantes.", "https://www.msdvetmanual.com/pt/special-pet-topics/intoxica%C3%A7%C3%A3o/intoxica%C3%A7%C3%A3o-por-medicamentos-humanos-de-venda-livre"),
 ("Permetrina em gatos", "Alguns antipulgas formulados para cães contêm permetrina, que pode causar intoxicação neurológica grave em gatos.", "https://www.msdvetmanual.com/pt/pharmacology/ectoparasiticidas/ectoparasiticidas-usados-em-animais-de-pequeno-porte"),
 ("Chocolate e metilxantinas", "Teobromina e cafeína podem causar sinais gastrointestinais, cardiovasculares e neurológicos. O risco depende do tipo, quantidade e peso.", "https://www.msdvetmanual.com/pt/toxicology/perigos-alimentares/toxicose-por-chocolate-em-animais"),
 ("Cebola e alho", "Podem causar dano oxidativo às hemácias e anemia hemolítica em cães e gatos.", "https://www.msdvetmanual.com/pt/toxicology/perigos-alimentares/intoxica%C3%A7%C3%A3o-por-alho-e-cebola-allium-spp-em-animais"),
 ("Uvas e uvas-passas", "Associadas a lesão renal aguda em cães. A quantidade tóxica é imprevisível; qualquer ingestão deve ser comunicada ao veterinário.", "https://www.msdvetmanual.com/pt/veterinary/special-pet-topics/intoxica%C3%A7%C3%A3o/perigos-alimentares"),
]

# Estado da sessão: os dados ficam apenas na sessão atual do Streamlit.
for key, default in [("pets", []), ("history", []), ("last_result", None)]:
    if key not in st.session_state: st.session_state[key] = default

st.markdown("""<style>
:root{--fp-green:#176b55;--fp-mint:#dff3e9;--fp-ink:#173b32;--fp-coral:#d94b4b;--fp-amber:#d98b24}
.stApp{background:linear-gradient(180deg,#f4faf6 0%,#f8fafc 55%,#eef6f1 100%);color:var(--fp-ink)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#e2f2e9 0%,#edf5f0 100%);border-right:1px solid #cfe2d6}
[data-testid="stMetric"]{background:rgba(255,255,255,.92);padding:18px;border:1px solid #d8e9df;border-radius:18px;box-shadow:0 5px 18px rgba(23,70,52,.06)}
div.stButton>button[kind="primary"]{background:linear-gradient(90deg,#176b55,#239b79);border:0;border-radius:12px;color:white;font-weight:700}
div.stButton>button{border-radius:12px;border-color:#c7ded0}
[data-testid="stExpander"]{background:rgba(255,255,255,.82);border:1px solid #dcebe2;border-radius:14px}
[data-testid="stForm"]{background:rgba(255,255,255,.72);border:1px solid #dcebe2;border-radius:16px;padding:18px}
.stTextInput input,.stNumberInput input,.stSelectbox>div>div{border-radius:10px}
h1,h2,h3{color:#174c3d}
.fp-hero{background:linear-gradient(120deg,#e1f5e9,#e5f4f8);padding:28px;border-radius:22px;border:1px solid #cfe7d9;margin-bottom:18px}
.fp-pill{display:inline-block;padding:5px 11px;border-radius:999px;font-weight:700;font-size:.78rem;margin:2px 0 8px 0}
.fp-red{background:#fee2e2;color:#991b1b}.fp-amber{background:#fff0cf;color:#8a4b08}.fp-green{background:#d9f4e5;color:#14633f}
.fp-card{background:white;border:1px solid #dcebe2;border-radius:16px;padding:16px;margin:8px 0;box-shadow:0 4px 14px rgba(25,70,50,.045)}
.small-note{font-size:.85rem;color:#68766c}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.image("logo.svg", width=86)
    st.markdown("# FarmaPet")
    st.caption("FARMACOLOGIA VETERINÁRIA")
    st.markdown("Ferramenta acadêmica de apoio a cálculos e consulta farmacológica.")
    page = st.radio("NAVEGAÇÃO", ["Início", "Dashboard", "Meus animais", "Calculadora", "Análise e resultados", "Medicamentos", "Interações", "Intoxicações", "Biblioteca científica", "Relatórios", "Sobre e referências"], label_visibility="collapsed", key="nav_page")
    st.divider()
    st.caption("Versão acadêmica 1.0 · Dados locais da sessão")

st.title("🐾 FarmaPet")
st.caption("Farmacologia veterinária em um só lugar · Cães e gatos")
st.warning("**Uso educativo e acadêmico.** O FarmaPet não prescreve medicamentos, não determina doses terapêuticas e não substitui avaliação médico-veterinária. Use apenas doses que constem de uma prescrição válida.")
if page != "Início":
    nav_back, nav_home = st.columns([1, 1])
    nav_back.button("← Voltar ao Dashboard", use_container_width=True, on_click=go_to_dashboard)
    nav_home.button("⌂ Início", use_container_width=True, on_click=go_to_home)

# Navegação e conteúdo
if page == "Início":
    st.subheader("Farmacologia veterinária com mais segurança")
    st.write("O FarmaPet organiza cálculos matemáticos de doses prescritas, informações farmacológicas e referências técnicas para tutores de cães e gatos.")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Objetivo principal")
        st.write("Apoiar a compreensão de cálculos de quantidade e concentração de medicamentos e facilitar o acesso a informações de segurança.")
    with c2:
        st.markdown("### Público-alvo")
        st.write("Tutores de cães e gatos e comunidade acadêmica. A ferramenta não substitui orientação veterinária.")
    st.button("INICIAR", type="primary", use_container_width=True, on_click=go_to_dashboard)
    st.button("SOBRE O APLICATIVO", use_container_width=True, on_click=go_to_about)
    st.info("O projeto foi desenvolvido como protótipo acadêmico. Nenhum dado de demonstração representa um paciente real.")

elif page == "Dashboard":
    st.subheader("Dashboard principal")
    hist = pd.DataFrame(st.session_state.history)
    pets = st.session_state.pets
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Animais cadastrados", len(pets))
    m2.metric("Cálculos na sessão", len(hist))
    m3.metric("Cães", sum(p['species']=='Cão' for p in pets))
    m4.metric("Gatos", sum(p['species']=='Gato' for p in pets))
    st.markdown("#### Atalhos")
    st.write("Use o menu lateral para cadastrar animais, calcular uma dose prescrita, consultar medicamentos ou exportar relatórios.")
    if len(hist):
        st.markdown("#### Últimos cálculos")
        st.dataframe(hist.head(5), use_container_width=True, hide_index=True)
        by_species = hist.groupby("Espécie").size().reset_index(name="Cálculos")
        fig = px.bar(by_species, x="Espécie", y="Cálculos", title="Cálculos registrados por espécie", text="Cálculos")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Fonte: registros realizados pelo usuário nesta sessão. Não são dados clínicos nem resultados de pesquisa.")
    else:
        st.info("Ainda não há cálculos nesta sessão. Faça um cálculo para gerar indicadores e gráficos reais a partir dos seus próprios registros.")

elif page == "Meus animais":
    st.subheader("Cadastro de animais")
    st.markdown('<div class="fp-hero"><h3>🐾 Perfil do seu companheiro</h3><p>Cadastre informações básicas para facilitar o preenchimento dos cálculos. A foto é opcional e permanece apenas na sessão atual.</p></div>', unsafe_allow_html=True)
    species = st.selectbox("Espécie", ["Cão", "Gato"], key="pet_species_new")
    dog_breeds = ["Vira-lata / Sem raça definida (SRD)","Labrador Retriever","Golden Retriever","Poodle","Shih-tzu","Yorkshire Terrier","Bulldog Francês","Bulldog Inglês","Dachshund (salsicha)","Pinscher","Pug","Beagle","Pastor Alemão","Border Collie","Rottweiler","Boxer","Lulu da Pomerânia (Spitz Alemão)","Maltês","Chihuahua","Cocker Spaniel","Outra / não listada"]
    cat_breeds = ["Vira-lata / Sem raça definida (SRD)","Persa","Siamês","Maine Coon","Ragdoll","Sphynx","Bengal","British Shorthair","Scottish Fold","Angorá","Himalaio","American Shorthair","Outra / não listada"]
    breed = st.selectbox("Raça", dog_breeds if species == "Cão" else cat_breeds)
    with st.form("pet_form", clear_on_submit=True):
        a,b = st.columns(2)
        name = a.text_input("Nome do animal")
        age = b.number_input("Idade aproximada (anos)", min_value=0.0, max_value=40.0, value=1.0, step=0.5)
        weight = a.number_input("Peso atual (kg)", min_value=0.01, max_value=150.0, value=1.0, step=0.1)
        photo = b.file_uploader("Foto do animal (opcional)", type=["png","jpg","jpeg","webp"], help="A imagem será mantida somente durante esta sessão do aplicativo.")
        submitted = st.form_submit_button("🐾 Cadastrar animal", type="primary", use_container_width=True)
    if submitted:
        if not name.strip(): st.error("Informe o nome do animal.")
        elif weight <= 0: st.error("O peso deve ser maior que zero.")
        else:
            photo_bytes = photo.getvalue() if photo is not None else None
            st.session_state.pets.append({"name":name.strip(),"species":species,"breed":breed,"age":age,"weight":weight,"photo":photo_bytes})
            st.success(f"{name.strip()} foi cadastrado nesta sessão!")
    if st.session_state.pets:
        st.markdown("#### Animais cadastrados")
        for idx, animal in enumerate(st.session_state.pets):
            with st.container(border=True):
                col_img, col_info = st.columns([1,3])
                if animal.get("photo"):
                    col_img.image(animal["photo"], use_container_width=True)
                else:
                    col_img.markdown("<div style='font-size:48px;text-align:center;padding:16px'>🐶</div>" if animal['species']=="Cão" else "<div style='font-size:48px;text-align:center;padding:16px'>🐱</div>", unsafe_allow_html=True)
                col_info.markdown(f"**{animal['name']}** · {animal['species']}")
                col_info.write(f"Raça: {animal['breed']}  |  Idade: {animal['age']:g} anos  |  Peso: {animal['weight']:g} kg")
        if st.button("Limpar cadastro da sessão", type="secondary"):
            st.session_state.pets=[]; st.rerun()
    st.caption("Privacidade: fotos e cadastros ficam apenas na memória da sessão do Streamlit. Não são enviados a bases externas e desaparecem ao encerrar a sessão.")

elif page == "Calculadora":
    st.subheader("Calculadora farmacológica")
    st.caption("Etapa 1 de 3 · Inserção dos dados → cálculo → resultado e histórico")
    st.progress(1/3)
    st.info("Informe exatamente os dados da prescrição veterinária e da embalagem. A ferramenta apenas calcula quantidades; não verifica adequação clínica da dose.")
    pets = st.session_state.pets
    options = ["Inserir manualmente"] + [f"{p['name']} ({p['species']})" for p in pets]
    selected = st.selectbox("Animal cadastrado (opcional)", options)
    pet = None
    if selected != "Inserir manualmente":
        pet = pets[options.index(selected)-1]
    col1,col2 = st.columns(2)
    species = col1.selectbox("Espécie", ["Cão", "Gato"], index=0 if not pet or pet['species']=="Cão" else 1)
    weight_default = float(pet['weight']) if pet else 1.0
    weight = col2.number_input("Peso (kg)", min_value=0.001, max_value=150.0, value=weight_default, step=0.1, format="%.3f")
    basis = st.selectbox("Base da prescrição", ["mg/kg por administração", "mg/kg por dia (dose diária total)"])
    dose = st.number_input("Dose prescrita (mg/kg)", min_value=0.000001, value=1.0, step=0.1, format="%.6f")
    freq = st.number_input("Administrações por dia (para dose diária)", min_value=1, max_value=24, value=2, step=1, help="Campo editável. Só é utilizado quando a prescrição está expressa em mg/kg por dia.")
    presentation = st.selectbox("Apresentação", ["Solução/suspensão (mg/mL)", "Suspensão (mg/5 mL)", "Comprimido (mg/comprimido)"])
    conc_label = {"Solução/suspensão (mg/mL)":"Concentração (mg/mL)","Suspensão (mg/5 mL)":"Concentração (mg/5 mL)","Comprimido (mg/comprimido)":"Concentração (mg/comprimido)"}[presentation]
    concentration = st.number_input(conc_label, min_value=0.000001, value=20.0, step=0.1, format="%.6f", key=f"concentration_{presentation}")
    st.caption({"Solução/suspensão (mg/mL)":"Informe o valor em miligramas por 1 mL, como aparece no rótulo.","Suspensão (mg/5 mL)":"Informe o valor em miligramas por 5 mL, como aparece no rótulo. A conversão é automática.","Comprimido (mg/comprimido)":"Informe quantos miligramas há em cada comprimido."}[presentation])
    calc_submit = st.button("CALCULAR", type="primary", use_container_width=True)
    if calc_submit:
        try:
            basis_key = "mg/kg por dia" if basis.startswith("mg/kg por dia") else "mg/kg por administração"
            presentation_key = {"Solução/suspensão (mg/mL)":"mg/mL", "Suspensão (mg/5 mL)":"mg/5 mL", "Comprimido (mg/comprimido)":"mg/comprimido"}[presentation]
            calc = calcular_quantidade(weight, dose, basis_key, int(freq), presentation_key, concentration)
            per_dose_mg = calc["mg_por_administracao"]
            per_unit = calc["quantidade_por_administracao"]
            unit = calc["unidade"]
            daily_total_mg = calc["total_diario_mg"]
            result = {"Data":datetime.now().strftime("%d/%m/%Y %H:%M"),"Animal":pet['name'] if pet else "Não vinculado","Espécie":species,"Peso (kg)":weight,"Dose (mg/kg)":dose,"Base":basis,"Frequência/dia":freq if daily_total_mg is not None else "Não usada","Apresentação":presentation,"Teor informado":concentration,"Princípio ativo por administração (mg)":per_dose_mg,"Quantidade por administração":per_unit,"Unidade":unit,"Total diário (mg)":daily_total_mg}
            st.session_state.last_result=result
            st.session_state.history.insert(0,result)
            st.session_state.history=st.session_state.history[:100]
            st.success("Cálculo matemático concluído e registrado nesta sessão.")
        except (ValueError, ZeroDivisionError) as exc: st.error(str(exc))
    if st.session_state.last_result:
        r=st.session_state.last_result
        st.markdown("### Resultado matemático")
        x,y,z=st.columns(3)
        x.metric("Quantidade por administração", f"{r['Quantidade por administração']:.6g} {r['Unidade']}")
        y.metric("Princípio ativo por administração", f"{r['Princípio ativo por administração (mg)']:.6g} mg")
        z.metric("Peso utilizado", f"{r['Peso (kg)']:.3g} kg")
        if r["Base"].startswith("mg/kg por dia"):
            st.write(f"Fórmula: (dose diária × peso) ÷ administrações/dia = ({r['Dose (mg/kg)']} × {r['Peso (kg)']}) ÷ {r['Frequência/dia']} = {r['Princípio ativo por administração (mg)']:.6g} mg por administração.")
        else:
            st.write(f"Fórmula: dose por administração × peso = {r['Dose (mg/kg)']} × {r['Peso (kg)']} = {r['Princípio ativo por administração (mg)']:.6g} mg por administração.")
        if r['Unidade']=="comprimido(s)" and abs(r['Quantidade por administração']-round(r['Quantidade por administração']))>1e-6:
            st.warning("Resultado fracionário teórico. Nem todo comprimido pode ser partido ou triturado. Confirme a divisibilidade e a formulação com o veterinário e a bula.")
        if r['Unidade']=="mL" and r['Quantidade por administração']<0.1:
            st.warning("Volume muito pequeno: confirme se o dispositivo de medição permite precisão adequada.")
        st.progress(1.0)
        st.error("Este resultado não confirma se o medicamento, a dose, a via, o intervalo ou a duração são apropriados para o animal. Confira a prescrição com o médico-veterinário.")
    if st.button("Limpar resultado da calculadora"):
        st.session_state.last_result = None
        st.rerun()

elif page == "Análise e resultados":
    st.subheader("Análise e visualização dos registros")
    hist=pd.DataFrame(st.session_state.history)
    uploaded = st.file_uploader("Importar histórico em CSV ou Excel (opcional)", type=["csv", "xlsx"], help="Use apenas arquivos sem dados pessoais identificáveis. A importação é usada nesta sessão e não é enviada a uma base externa.")
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            st.success(f"Arquivo importado: {len(imported)} linhas e {len(imported.columns)} colunas.")
            st.dataframe(imported.head(100), use_container_width=True, hide_index=True)
            st.caption("A importação exibe e organiza os dados fornecidos. Ela não valida prescrição nem interpreta dados clínicos automaticamente.")
        except Exception as exc:
            st.error(f"Não foi possível ler o arquivo. Confira o formato e as colunas. Detalhe: {exc}")
    if hist.empty:
        st.info("Faça pelo menos um cálculo para habilitar gráficos e tabelas. Os dados de demonstração podem ser carregados abaixo e são fictícios.")
        if st.button("Carregar dados fictícios de demonstração"):
            st.session_state.history=[
              {"Data":"DEMO 01/11/2026","Animal":"Luna (FICTÍCIO)","Espécie":"Cão","Peso (kg)":8.0,"Dose (mg/kg)":5.0,"Base":"mg/kg por administração","Frequência/dia":"Não usada","Apresentação":"Solução/suspensão (mg/mL)","Teor informado":10.0,"Princípio ativo por administração (mg)":40.0,"Quantidade por administração":4.0,"Unidade":"mL","Total diário (mg)":None},
              {"Data":"DEMO 02/11/2026","Animal":"Mimi (FICTÍCIO)","Espécie":"Gato","Peso (kg)":4.0,"Dose (mg/kg)":2.0,"Base":"mg/kg por administração","Frequência/dia":"Não usada","Apresentação":"Suspensão (mg/5 mL)","Teor informado":20.0,"Princípio ativo por administração (mg)":8.0,"Quantidade por administração":2.0,"Unidade":"mL","Total diário (mg)":None},
              {"Data":"DEMO 03/11/2026","Animal":"Toby (FICTÍCIO)","Espécie":"Cão","Peso (kg)":12.0,"Dose (mg/kg)":1.0,"Base":"mg/kg por dia (dose diária total)","Frequência/dia":2,"Apresentação":"Comprimido (mg/comprimido)","Teor informado":6.0,"Princípio ativo por administração (mg)":6.0,"Quantidade por administração":1.0,"Unidade":"comprimido(s)","Total diário (mg)":12.0},
            ]
            st.rerun()
    else:
        st.caption("Fonte: cálculos registrados nesta sessão. Se aparecer ‘DEMO’ ou ‘FICTÍCIO’, os registros são dados simulados para demonstração e não representam pacientes reais.")
        a,b=st.columns(2)
        species_counts=hist["Espécie"].value_counts().rename_axis("Espécie").reset_index(name="Registros")
        fig=px.bar(species_counts,x="Espécie",y="Registros",title="Distribuição de cálculos por espécie",text="Registros")
        st.plotly_chart(fig,use_container_width=True)
        if "Peso (kg)" in hist:
            fig2=px.histogram(hist,x="Peso (kg)",color="Espécie",nbins=8,title="Distribuição dos pesos informados",labels={"Peso (kg)":"Peso (kg)"})
            st.plotly_chart(fig2,use_container_width=True)
        st.markdown("#### Tabela dinâmica dos resultados")
        st.dataframe(hist,use_container_width=True,hide_index=True)
        st.markdown("#### Interpretação descritiva")
        st.write(f"Foram registrados {len(hist)} cálculos nesta sessão. {int((hist['Espécie']=='Cão').sum())} registros correspondem a cães e {int((hist['Espécie']=='Gato').sum())} a gatos. O peso médio dos registros é {hist['Peso (kg)'].mean():.2f} kg.")
        st.caption("Esta descrição resume os dados inseridos. Não representa inferência clínica, eficácia, segurança terapêutica ou evidência epidemiológica.")

elif page == "Medicamentos":
    st.subheader("Guia farmacológico")
    st.write("Consulte informações gerais sobre princípios ativos, classes farmacológicas, usos descritos na medicina veterinária e possíveis riscos. Esta área é educativa: não indica qual medicamento deve ser usado nem substitui a avaliação do médico-veterinário.")
    st.info("🔴 Alto risco ou não indicado para automedicação   |   🟠 Exige avaliação veterinária   |   🟢 Há usos veterinários descritos, sempre sob prescrição")
    q = st.text_input("Buscar medicamento", placeholder="Digite o nome, a classe ou a espécie...")
    filtered = [m for m in MEDS if q.casefold() in (m['name'] + m['class'] + m['species'] + m['use'] + m['risk']).casefold()]
    if not filtered:
        st.warning("Nenhum medicamento encontrado. Confira a escrita ou tente outro termo.")
    for med in filtered:
        status = med['status']
        if "Alto risco" in status:
            badge_label = "🔴 ALTO RISCO · NÃO AUTOMEDICAR"
        elif med['name'] in ["Omeprazol", "Famotidina", "Sucralfato"]:
            badge_label = "🟢 USO VETERINÁRIO DESCRITO · SOB PRESCRIÇÃO"
        else:
            badge_label = "🟠 EXIGE AVALIAÇÃO VETERINÁRIA"
        with st.container(border=True):
            st.markdown(f"#### {med['name']}")
            st.caption(badge_label)
            st.markdown(f"**Classe farmacológica:** {med['class']}")
            st.markdown(f"**Espécies e observações:** {med['species']}")
            st.markdown(f"**Uso descrito:** {med['use']}")
            st.markdown(f"**Precauções e riscos:** {med['risk']}")
            st.markdown(f"[Consultar fonte técnica]({med['url']})")
    st.caption("A classificação verde não significa que o medicamento esteja liberado para uso doméstico. A indicação, dose, via e duração dependem de avaliação veterinária.")

elif page == "Interações":
    st.subheader("Consulta limitada de interações")
    st.warning("Esta base contém apenas algumas combinações documentadas. Ausência de alerta não significa ausência de interação. Não inicie, suspenda ou combine medicamentos com base apenas nesta consulta.")
    labels=sorted(set([x[0] for x in INTERACTIONS]+[x[1] for x in INTERACTIONS]+["Outro/não listado"]))
    a,b=st.columns(2)
    drug_a=a.selectbox("Classe ou medicamento 1",labels)
    drug_b=b.selectbox("Classe ou medicamento 2",labels,index=1 if len(labels)>1 else 0)
    if st.button("Consultar combinação",type="primary"):
        matches=[x for x in INTERACTIONS if (x[0]==drug_a and x[1]==drug_b) or (x[0]==drug_b and x[1]==drug_a)]
        if matches:
            for m in matches: st.error(f"**{m[0]} + {m[1]}**\n\n{m[2]}\n\nFonte: {m[3]} · [Consultar]({m[4]})")
        else: st.info("Não há correspondência cadastrada para esta combinação. Isso não comprova que seja segura; consulte uma base farmacológica veterinária e um profissional.")
    st.markdown("#### Combinações cadastradas")
    st.dataframe(pd.DataFrame([{"Combinação":f"{x[0]} + {x[1]}","Risco descrito":x[2],"Fonte":x[3]} for x in INTERACTIONS]),use_container_width=True,hide_index=True)

elif page == "Intoxicações":
    st.subheader("Central de prevenção de intoxicações")
    st.markdown('<div class="fp-hero"><h3>Reconheça os perigos</h3><p>Medicamentos humanos, produtos de limpeza, plantas, alimentos e antiparasitários inadequados podem provocar intoxicações em cães e gatos. Os efeitos variam conforme a substância, a quantidade, a espécie, o peso e o tempo decorrido desde o contato ou ingestão; alguns sinais também podem demorar a aparecer. Por isso, diante de uma suspeita, não espere o animal apresentar sintomas: afaste-o da fonte e procure orientação veterinária imediatamente, levando a embalagem ou o rótulo do produto sempre que possível.</p></div>', unsafe_allow_html=True)
    st.error("SUSPEITA DE INTOXICAÇÃO: procure atendimento veterinário imediatamente. Não provoque vômito nem administre leite, carvão ativado, medicamentos ou receitas caseiras por conta própria.")
    st.markdown('<span class="fp-pill fp-red">🔴 Perigo / evitar exposição</span> &nbsp; <span class="fp-pill fp-amber">🟠 Risco dependente da dose e contexto</span>', unsafe_allow_html=True)
    tox_query=st.text_input("🔎 Buscar substância ou alimento", placeholder="Ex.: chocolate, antipulgas, analgésico...")
    for name,desc,url in TOXINS:
        if tox_query.lower() not in (name+desc).lower(): continue
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.markdown('<span class="fp-pill fp-red">🔴 POTENCIALMENTE TÓXICO · MANTER AFASTADO</span>', unsafe_allow_html=True)
            st.write(desc)
            st.markdown(f"[Consultar referência técnica]({url})")
    st.markdown("#### O que fazer diante de uma possível exposição")
    steps = ["Afaste o animal da fonte, sem se colocar em risco.","Guarde a embalagem ou fotografe o rótulo e os ingredientes.","Anote o horário aproximado e a quantidade possivelmente ingerida.","Informe ao serviço veterinário a espécie e o peso do animal.","Não espere sintomas para buscar orientação profissional."]
    for item in steps: st.markdown(f"- {item}")
    st.caption("As classificações são educativas e não estimam uma dose tóxica individual. Em caso de exposição, a orientação veterinária é indispensável.")

elif page == "Biblioteca científica":
    st.subheader("Biblioteca científica e técnica")
    st.caption("Os títulos em português são traduções descritivas quando a publicação original está em inglês. O link direciona para a fonte original.")
    category=st.selectbox("Filtrar por assunto",["Todos"]+sorted(set(x['category'] for x in REFERENCES)))
    for ref in REFERENCES:
        if category!="Todos" and ref['category']!=category: continue
        st.markdown(f"**{ref['title']}**  \n{ref['source']} · {ref['category']}  \n[ Acessar fonte original ]({ref['url']})")
        st.divider()

elif page == "Relatórios":
    st.subheader("Relatórios e exportação")
    hist=pd.DataFrame(st.session_state.history)
    if hist.empty: st.info("Não há registros para exportar. Realize um cálculo ou carregue dados fictícios na tela Análise e resultados.")
    else:
        st.dataframe(hist,use_container_width=True,hide_index=True)
        csv=hist.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Baixar CSV",csv,file_name="farmapet_registros.csv",mime="text/csv")
        xlsx_buffer=BytesIO()
        with pd.ExcelWriter(xlsx_buffer,engine="openpyxl") as writer: hist.to_excel(writer,index=False,sheet_name="Registros")
        st.download_button("Baixar Excel",xlsx_buffer.getvalue(),file_name="farmapet_registros.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        report="FARMAPET — RELATÓRIO DE CÁLCULOS\nGerado em: "+datetime.now().strftime("%d/%m/%Y %H:%M")+"\n\nUso educativo. Não substitui prescrição veterinária.\n\n"+hist.to_string(index=False)
        st.download_button("Baixar relatório TXT",report.encode("utf-8"),file_name="farmapet_relatorio.txt",mime="text/plain")
        pdf_buffer=BytesIO()
        doc=SimpleDocTemplate(pdf_buffer,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=40,bottomMargin=40)
        styles=getSampleStyleSheet()
        story=[Paragraph("FarmaPet — Relatório de cálculos",styles["Title"]),Spacer(1,10),Paragraph("Gerado em: "+datetime.now().strftime("%d/%m/%Y %H:%M"),styles["Normal"]),Spacer(1,8),Paragraph("Uso educativo. Os resultados são matemáticos e não validam adequação clínica, prescrição ou segurança terapêutica.",styles["BodyText"]),Spacer(1,12)]
        pdf_data=[[str(c) for c in hist.columns]]
        for _,row in hist.iterrows(): pdf_data.append([str(row.get(c,""))[:45] for c in hist.columns])
        # Tabela resumida para caber em página A4.
        keep=[c for c in ["Data","Animal","Espécie","Peso (kg)","Dose (mg/kg)","Quantidade por administração","Unidade"] if c in hist.columns]
        pdf_data=[[str(c) for c in keep]]+[[str(row.get(c,""))[:35] for c in keep] for _,row in hist.iterrows()]
        table=Table(pdf_data,repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#426b50")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#d9e2d8")),("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f2f6f1")])]))
        story.append(table)
        doc.build(story)
        st.download_button("Baixar relatório PDF",pdf_buffer.getvalue(),file_name="farmapet_relatorio.pdf",mime="application/pdf")
        st.caption("O relatório registra os dados e resultados matemáticos. Não valida adequação clínica das doses.")

elif page == "Sobre e referências":
    st.subheader("Sobre o FarmaPet")
    st.markdown("**Equipe responsável:** Ana Luiza Laet · Éwelin Marcele · Mikaelly Ketilley · Thatiana Aragão")
    st.write("**Finalidade:** protótipo acadêmico de apoio educativo a cálculos matemáticos de doses prescritas e consulta de informações farmacológicas veterinárias para cães e gatos.")
    st.write("**Área:** Ciências Farmacêuticas, Farmacologia Veterinária e Toxicologia.")
    st.write("**Tecnologias:** Python, Streamlit, Pandas, NumPy, Plotly, openpyxl e ReportLab. Exportação CSV, Excel, TXT e PDF.")
    st.write("**Bases consultadas:** Manual MSD de Veterinária, PubMed, Cornell University, WSAVA, ACVIM, FDA e periódicos científicos. Não há conexão automática em tempo real com essas bases nesta versão.")
    st.write("**Inteligência Artificial:** não há modelo de IA integrado nesta versão. O texto e a organização do protótipo podem ter recebido auxílio de IA e precisam de validação humana; nenhuma interpretação automatizada é apresentada como diagnóstico ou evidência nova.")
    st.write("**Limitações:** interações cadastradas são parciais; fichas são resumos educativos; cálculos não avaliam adequação terapêutica; não há autenticação, sincronização, backend clínico ou armazenamento persistente seguro.")
    st.write("**Privacidade:** não insira nome completo do tutor, endereço, telefone ou outros dados pessoais. Os dados ficam na sessão atual e podem desaparecer ao reiniciar o aplicativo.")
    st.markdown("#### Referências utilizadas")
    for ref in REFERENCES: st.markdown(f"- {ref['source']}. *{ref['title']}*. Disponível em: {ref['url']}.")
    st.caption("FarmaPet · Versão acadêmica 1.0 · Novembro de 2026")

st.divider()
st.caption("FarmaPet · Ferramenta acadêmica e educativa · Versão 1.0 · Não substitui avaliação médico-veterinária.")
