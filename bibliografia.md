# Bibliografía

> Documento de registro de fuentes consultadas y referenciadas durante la elaboración de la memoria del TFG.  
> Formato: APA 7ª edición.

---

## Modelos Estadísticos de Series Temporales

**[1]** Box, G. E. P., & Jenkins, G. M. (1970). *Time series analysis: Forecasting and control*. Holden-Day.

> Obra fundacional de los modelos ARIMA. Define el proceso de identificación, estimación y validación (metodología Box-Jenkins) que sigue siendo la base teórica de los modelos ARIMA/SARIMA implementados en este proyecto.

---

**[2]** Taylor, S. J., & Letham, B. (2018). Forecasting at scale. *The American Statistician*, *72*(1), 37–45. https://doi.org/10.1080/00031305.2017.1380080

> Artículo original de Meta (Facebook) que presenta el modelo Prophet. Describe la filosofía de diseño orientada a analistas no expertos, la descomposición aditiva de la serie (tendencia + estacionalidad + festividades) y la robustez ante datos faltantes y valores atípicos.

---

**[3]** Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/

> Libro de referencia en forecasting moderno. Cubre modelos ARIMA, suavizado exponencial, descomposición estacional y criterios de selección de modelos (AIC, BIC). Disponible en abierto en la URL indicada.

---

**[4]** Yule, G. U. (1927). On a method of investigating periodicities in disturbed series, with special reference to Wolfer's sunspot numbers. *Philosophical Transactions of the Royal Society of London A*, *226*, 267–298. https://doi.org/10.1098/rsta.1927.0007

> Primer trabajo formal sobre procesos autoregresivos (AR), que constituye la base del componente AR de los modelos ARIMA.

---

## Aplicaciones de Forecasting en el Ámbito Sanitario

**[5]** Rostami-Tabar, B., Babai, M. Z., Syntetos, A., & Ducq, Y. (2021). Demand forecasting for healthcare: Lessons from and for other sectors. *Foresight: The International Journal of Applied Forecasting*, *60*, 12–18.

> Revisión de modelos de predicción de demanda en el sector sanitario. Justifica la aplicabilidad del forecasting estadístico en la planificación hospitalaria (listas de espera, asignación de quirófanos).

---

**[6]** Tandberg, D., & Qualls, C. (1995). Time series forecasts of emergency department patient volume, length of stay, and acuity. *Annals of Emergency Medicine*, *25*(5), 657–661. https://doi.org/10.1016/S0196-0644(95)70278-0

> Estudio pionero sobre el uso de modelos ARIMA para predecir la demanda de urgencias hospitalarias.

---

## Librerías y Herramientas de Software

**[7]** Meta Open Source. (2023). *Prophet: Forecasting at scale* [Software]. GitHub. https://github.com/facebook/prophet

> Repositorio oficial de la librería Prophet. Documentación técnica de la API, parámetros de configuración y ejemplos de uso.

---

**[8]** Smith, T. G., et al. (2017). *pmdarima: ARIMA estimators for Python* [Software]. GitHub. https://github.com/alkaline-ml/pmdarima

> Librería que implementa `auto_arima` en Python, utilizada en este proyecto para la selección automática de órdenes (p, d, q) del modelo ARIMA/SARIMA por criterio AIC.

---

**[9]** Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference (SciPy 2010)*, 92–96. https://doi.org/10.25080/Majora-92bf1922-011

> Motor estadístico subyacente a pmdarima. Proporciona la implementación de ARIMA/SARIMA y la descomposición estacional (`seasonal_decompose`) utilizada en la detección de estacionalidad.

---

**[10]** Ramírez, S. (2023). *FastAPI* [Software, v0.100+]. https://fastapi.tiangolo.com/

> Framework web Python utilizado para construir la API REST del proyecto. Basado en Starlette y Pydantic, con generación automática de documentación OpenAPI.

---

**[11]** SQLAlchemy authors. (2023). *SQLAlchemy: The Python SQL toolkit and Object Relational Mapper* [Software]. https://www.sqlalchemy.org/

> ORM utilizado para la gestión de la base de datos (SQLite en desarrollo, PostgreSQL en producción).

---

**[12]** Pydantic authors. (2023). *Pydantic v2: Data validation using Python type hints* [Software]. https://docs.pydantic.dev/

> Librería de validación de datos utilizada para los esquemas de entrada/salida de la API y la gestión de configuración mediante `BaseSettings`.

---

## Seguridad en APIs REST

**[13]** Jones, M., Bradley, J., & Sakimura, N. (2015). *JSON Web Token (JWT)*. RFC 7519. Internet Engineering Task Force (IETF). https://datatracker.ietf.org/doc/html/rfc7519

> Especificación estándar de JWT, utilizado en este proyecto para la autenticación y los tokens de recuperación de contraseña.

---

**[14]** OWASP Foundation. (2021). *OWASP Top Ten 2021*. https://owasp.org/www-project-top-ten/

> Referencia de las vulnerabilidades más críticas en aplicaciones web. Empleada como guía para las decisiones de seguridad del proyecto (hashing de contraseñas, validación de entradas, control de acceso).

---

**[15]** Provos, N., & Mazières, D. (1999). A future-adaptable password scheme. *Proceedings of the USENIX Annual Technical Conference*, 81–91.

> Artículo original del algoritmo bcrypt, utilizado en este proyecto para el hashing de contraseñas con factor de coste 12.

---

## Métricas de Evaluación de Modelos

**[16]** Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting*, *22*(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001

> Análisis comparativo de métricas de error de forecasting (MAE, RMSE, MAPE, MASE). Referencia para justificar el uso de MAE, RMSE y MAPE en la evaluación de los modelos del proyecto.

---

**[17]** Akaike, H. (1974). A new look at the statistical model identification. *IEEE Transactions on Automatic Control*, *19*(6), 716–723. https://doi.org/10.1109/TAC.1974.1100705

> Artículo original del Criterio de Información de Akaike (AIC), utilizado en este proyecto para la selección automática de órdenes ARIMA mediante `auto_arima`.

---

**[18]** Schwarz, G. (1978). Estimating the dimension of a model. *The Annals of Statistics*, *6*(2), 461–464. https://doi.org/10.1214/aos/1176344136

> Artículo original del Criterio de Información Bayesiano (BIC), complementario al AIC en la selección de modelos ARIMA.

---

## Contenedorización y Despliegue

**[19]** Merkel, D. (2014). Docker: Lightweight Linux containers for consistent development and deployment. *Linux Journal*, *2014*(239), 2.

> Artículo de referencia sobre Docker, tecnología empleada para la contenedorización y despliegue del sistema.

---

*Última actualización: abril 2026*
