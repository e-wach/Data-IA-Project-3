# 🧠 BetMaestro – Data Project 3

[![Ver demo en YouTube](https://img.shields.io/badge/%F0%9F%93%BD%20Demo%20en%20YouTube-red?style=for-the-badge)](https://youtu.be/gpr9XA1yVy4)
[![Ver vídeo promocional](https://img.shields.io/badge/%F0%9F%8E%A5%20Vídeo%20promocional-purple?style=for-the-badge)](https://www.youtube.com/watch?v=MBa65teaebc&ab_channel=CokeStuyck)

---

## 🎯 Descripción del proyecto

**BetMaestro** nace con un objetivo claro: ayudar a los usuarios a tomar mejores decisiones en el mundo de las apuestas deportivas. Con este proyecto, transformamos datos en valor, automatizando todo el flujo de ingestión, procesamiento y almacenamiento de información deportiva desde diferentes fuentes, y sentando las bases para futuras aplicaciones basadas en Inteligencia Artificial.

---

## 🧱 Arquitectura técnica

El sistema está completamente desplegado sobre **Google Cloud Platform** y automatizado con **Terraform**.  
Nuestra solución sigue un enfoque modular y escalable, compuesto por:

🔹 **APIs externas**  
Datos obtenidos desde [NBA API](https://github.com/swar/nba_api) y [SportsData.io](https://sportsdata.io/), incluyendo:

- Estadísticas de partidos
- Cuotas de apuestas (odds)
- Lesiones de jugadores

🔹 **Cloud Functions**  
Funciones en Python con distintos triggers:

- **Pub/Sub**: para procesar datos en tiempo real
- **Cloud Storage**: para cargar históricos desde CSV

🔹 **Pub/Sub**  
Sistema de mensajería que permite desacoplar los productores y consumidores de datos.

🔹 **BigQuery**  
Almacenamiento analítico para procesamiento masivo y exploración de datos. Preparado para usarse en modelos de IA.

🔹 **Cloud SQL (PostgreSQL)**  
Base de datos relacional para guardar información estructurada y accesible para el backend.

🔹 **Cloud Run + Docker**  
Nuestras APIs internas también se despliegan automáticamente como contenedores.

🔹 **Streamlit**  
Frontend interactivo para visualizar insights y explorar los datos de manera sencilla y accesible.

---

## 🤖 Inteligencia Artificial (visión futura)

Aunque el foco actual ha sido construir una infraestructura sólida, BetMaestro ya está preparado para ser integrado con modelos de predicción. Gracias al almacenamiento estructurado y automatizado, se pueden desarrollar:

- Modelos de predicción de resultados o cuotas
- Sistemas de alerta en tiempo real
- Recomendadores personalizados según patrones de apuesta

Todo esto será posible gracias a la calidad y continuidad del pipeline de datos que hemos diseñado.

---

## 🚀 Despliegue

El despliegue completo se realiza en unos minutos con:

```bash
terraform init
terraform apply
