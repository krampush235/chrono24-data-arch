-- Base de datos del marketplace (on-premise)
CREATE DATABASE IF NOT EXISTS chrono_oltp;
USE chrono_oltp;

-- Marcas de relojes
CREATE TABLE marcas (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre   VARCHAR(80) NOT NULL UNIQUE,
    pais     VARCHAR(50)
);

-- Personas o tiendas que venden relojes
CREATE TABLE vendedores (
    id_vendedor    INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(120) NOT NULL,
    tipo_vendedor  VARCHAR(20),
    pais           VARCHAR(50),
    correo         VARCHAR(120) UNIQUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personas que compran relojes
CREATE TABLE compradores (
    id_comprador   INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(120) NOT NULL,
    correo         VARCHAR(120) UNIQUE,
    pais           VARCHAR(50),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anuncios de relojes publicados
CREATE TABLE anuncios (
    id_anuncio        INT AUTO_INCREMENT PRIMARY KEY,
    id_vendedor       INT,
    id_marca          INT,
    modelo            VARCHAR(120) NOT NULL,
    condicion         VARCHAR(20),
    precio_eur        DECIMAL(12,2) NOT NULL,
    estado            VARCHAR(15) DEFAULT 'activo',
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vendedor) REFERENCES vendedores(id_vendedor),
    FOREIGN KEY (id_marca)    REFERENCES marcas(id_marca)
);

-- Pedidos realizados por los compradores
CREATE TABLE pedidos (
    id_pedido      INT AUTO_INCREMENT PRIMARY KEY,
    id_anuncio     INT,
    id_comprador   INT,
    fecha_pedido   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_eur      DECIMAL(12,2) NOT NULL,
    comision_eur   DECIMAL(12,2),
    estado         VARCHAR(20),
    FOREIGN KEY (id_anuncio)   REFERENCES anuncios(id_anuncio),
    FOREIGN KEY (id_comprador) REFERENCES compradores(id_comprador)
);