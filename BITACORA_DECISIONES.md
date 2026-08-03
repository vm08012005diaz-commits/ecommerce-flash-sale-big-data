# Bitácora de decisiones técnicas

Durante el desarrollo fui tomando decisiones para que el proyecto pudiera funcionar de forma sencilla en una computadora y, al mismo tiempo, demostrara los temas estudiados en clase.

## Generación de datos

Decidí generar los intentos de compra desde una aplicación web. Incluí un envío individual para probar un evento y un envío masivo para simular el aumento de clientes durante una venta flash. En mis pruebas utilicé lotes de 6,000 intentos o más.

Los productos no aparecen con la misma frecuencia. Algunos tienen más demanda que otros y la cantidad solicitada también cambia. Hice esto para que los datos no fueran completamente uniformes y se parecieran más a una situación real.

## Uso de Kafka

Elegí un solo topic dividido en seis particiones. Cada evento utiliza el identificador del producto como clave. Esto permite que Kafka distribuya el trabajo y mantenga juntos los eventos que pertenecen al mismo producto.

La otra opción era crear un topic diferente para cada producto, pero la descarté porque sería más difícil de administrar cuando aumentara la cantidad de productos.

## Almacenamiento

Elegí MongoDB porque los eventos se manejan como documentos JSON y su estructura puede cambiar sin tener que modificar muchas tablas. También facilita guardar los eventos y consultar los resultados que utiliza el dashboard.

Consideré usar una base de datos relacional como PostgreSQL, pero para este proyecto preferí MongoDB por la flexibilidad de los documentos.

## Datos repetidos o incorrectos

Cada evento tiene un `event_id` único. Lo utilizo para evitar que un intento repetido se cuente dos veces. Cuando un evento contiene información incorrecta, se envía a una cola separada llamada DLQ para no detener todo el procesamiento.

## Visualización

El dashboard muestra el stock, los intentos recibidos, las unidades solicitadas y el estado de cada producto. Cuando las unidades solicitadas superan el inventario, el producto aparece en sobreventa. Esta fue la forma más clara que encontré para observar el resultado del procesamiento.

## Resultado de la prueba

Probé el sistema enviando intentos individuales y lotes de 6,000 eventos o más. Kafka recibió los eventos, el consumidor los procesó y el dashboard actualizó el balance de los productos. Al aumentar la cantidad de intentos pude observar productos en estado de sobreventa.
