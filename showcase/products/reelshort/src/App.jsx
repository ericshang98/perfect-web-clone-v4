import { useEffect, useState } from "react";

// Exact destinations persisted from the accepted capture. These intentionally
// include the source's nested, percent-encoded episode paths and play tokens.
const capturedShelfUrls = {
  51000879: "https://www.reelshort.com/es/shelf/nuevos-lanzamientos-short-movies-dramas-51000879",
  51000880: "https://www.reelshort.com/es/shelf/clasificaci%C3%B3n-short-movies-dramas-51000880",
  51000881: "https://www.reelshort.com/es/shelf/serie-doblada-short-movies-dramas-51000881",
  51000882: "https://www.reelshort.com/es/shelf/identidad-oculta-short-movies-dramas-51000882",
  51000883: "https://www.reelshort.com/es/shelf/relaci%C3%B3n-tab%C3%BA-short-movies-dramas-51000883",
  51000884: "https://www.reelshort.com/es/shelf/beb%C3%A9s-y-embarazos-short-movies-dramas-51000884",
  51000885: "https://www.reelshort.com/es/shelf/amor-a-primera-vista-short-movies-dramas-51000885",
  51000886: "https://www.reelshort.com/es/shelf/g%C3%A9nero-masculino-short-movies-dramas-51000886",
  51000887: "https://www.reelshort.com/es/shelf/hombre-lobo-y-vampiro-short-movies-dramas-51000887",
  51000888: "https://www.reelshort.com/es/shelf/historias-de-asia-short-movies-dramas-51000888",
};

const capturedEpisodeUrls = {
  "6a50cb594a37b7e5ea0c0c76": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-pap%C3%A1-soy-tu-estrella-de-la-suerte-6a50cb594a37b7e5ea0c0c76-0nf96ubpnb?playTime=1",
  "6a574266f3666a49a80f1eaa": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-esposa-falsa-del-multimillonario-6a574266f3666a49a80f1eaa-vqyqwezemx?playTime=1",
  "6a57383d6238eeb3740747b8": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-hermandad-de-mentiras-juramento-de-venganza-6a57383d6238eeb3740747b8-8s3tfk0jmu?playTime=1",
  "6a4f1b867798749acb0ce014": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-dulce-tentaci%C3%B3n-6a4f1b867798749acb0ce014-nzthzat8kd?playTime=1",
  "6a50c9304ca0f84fb700933d": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-amor-en-las-cenizas-de-lo-nuestro-6a50c9304ca0f84fb700933d-aq2m181f3r?playTime=1",
  "6a50c3945f279ed277001990": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-hija-de-zeus-6a50c3945f279ed277001990-2smfbdmdaw?playTime=1",
  "6a50c6c74053a2c0ee0ff7a3": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-ni%C3%B1era-de-mi-guapo-acosador-6a50c6c74053a2c0ee0ff7a3-8arxwab8fu?playTime=1",
  "6a3e412b58a5eabbce082cd2": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-no-es-la-novia-que-%C3%A9l-quer%C3%ADa-6a3e412b58a5eabbce082cd2-x8fmn0zc4d?playTime=1",
  "6a3e3fe2e6b933aba2070614": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-genio-de-la-l%C3%A1mpara-bajo-contrato-6a3e3fe2e6b933aba2070614-bdomldmrwy?playTime=1",
  "69be36e15fa05aa0a5090d3f": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-despertar-del-abismo-69be36e15fa05aa0a5090d3f-l9a98ujqnl?playTime=1",
  "68f6f7c5794cc55960091d71": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-cuenta-regresiva-por-la-vida-rescate-a-30-000-pies-68f6f7c5794cc55960091d71-4p9byhhevg?playTime=1",
  "6a291f9b53df79f3880404bd": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-capit%C3%A1n-de-hockey-que-me-odia-6a291f9b53df79f3880404bd-9t9hzmf0zh?playTime=1",
  "69dc921b1015a88977031807": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-esc%C3%A1ndalo-en-el-probador-69dc921b1015a88977031807-sec0li5rhy?playTime=1",
  "69b7d5c40c8c1196c0003b54": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-su-hermano-perdido-en-el-espacio-69b7d5c40c8c1196c0003b54-klubgew5aj?playTime=1",
  "69859804c95814e19b0ad4a8": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-consentida-de-los-tres-magnates-69859804c95814e19b0ad4a8-ygketwh2hc?playTime=1",
  "68357a414a236167a9025c32": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-shhh-profesor-por-favor-no-lo-digas-68357a414a236167a9025c32-0001?playTime=1",
  "6a291fc053df79f38804054d": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-waterboy-segunda-oportunidad-6a291fc053df79f38804054d-0001?playTime=1",
  "69def17ad64c48cfe60c8615": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-ap%C3%A1rtense-lleg%C3%B3-el-magnate-69def17ad64c48cfe60c8615-ew2dbk1mag?playTime=1",
  "694cd7715f7166c5760b6c2d": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-aguador-694cd7715f7166c5760b6c2d-0001?playTime=1",
  "69421d38a16cee9b6f0db474": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-rey-guardi%C3%A1n-discreto-69421d38a16cee9b6f0db474-1948es1za6?playTime=1",
  "64828858d5f75b406b6357d8": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-nunca-te-divorcies-de-una-heredera-multimillonaria-secreta-64828858d5f75b406b6357d8-buxznyw0?playTime=1",
  "6836b7ce5bff06fba908bd20": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-reina-ceo-la-venganza-de-una-madre-6836b7ce5bff06fba908bd20-s49rasvs7n?playTime=1",
  "694a2ca1adfd9f446d026951": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-lo-que-el-viento-se-llev%C3%B3-694a2ca1adfd9f446d026951-8rk7akeb28?playTime=1",
  "677e28b639d7346eda0aebfc": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-uy-estoy-enamorada-de-mi-hermanastro-677e28b639d7346eda0aebfc-0001?playTime=1",
  "699fa82c6e46de4a5b09edc8": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-fingiendo-inocencia-conquistando-su-coraz%C3%B3n-699fa82c6e46de4a5b09edc8-yo6ghaumdo?playTime=1",
  "6a1fbe4b23381626270c684c": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-papi-alfa-hazme-tuya-6a1fbe4b23381626270c684c-gb40k2qbq1?playTime=1",
  "6a0ad7fd9d2e9a432f0331ed": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-enamor%C3%A1ndome-de-mi-hermanastro-mi-enemigo-6a0ad7fd9d2e9a432f0331ed-ks2jvp22ii?playTime=1",
  "681d6b63ac0e0dc6070023d8": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-me-enamor%C3%A9-del-mejor-amigo-de-mi-hermano-681d6b63ac0e0dc6070023d8-yk9rosrsd2?playTime=1",
  "67eb4d2cbfe804cbeb02ba58": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-virgen-y-el-millonario-67eb4d2cbfe804cbeb02ba58-mbnilv6nq4?playTime=1",
  "6a2779b6436fd9cc500e90ca": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-una-noche-con-el-general-del-imperio-6a2779b6436fd9cc500e90ca-x5ex0plg96?playTime=1",
  "67bc1a9c2e3827da9c0c0b02": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-estoy-embarazada-separemonos-67bc1a9c2e3827da9c0c0b02-rjfzz4i27u?playTime=1",
  "69de16fcea1c6793640283a9": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-ternura-cruel-del-jefe-mafioso-69de16fcea1c6793640283a9-mf4kkjbjdz?playTime=1",
  "6882eb265b6d9601ab098cbc": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-accidentalmente-embarazada-del-alfa-6882eb265b6d9601ab098cbc-v1t4scb2a6?playTime=1",
  "69c49971e92f4783e60e3a19": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-despu%C3%A9s-del-divorcio-soy-consentida-por-tres-hermanos-69c49971e92f4783e60e3a19-x5lugtkbgc?playTime=1",
  "671b0b5a4c2513f2b1097c8c": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-su-%C3%BAnico-amor-671b0b5a4c2513f2b1097c8c-xz8wupgxnm?playTime=1",
  "69855069cad2c6f86d0cf93d": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-mi-beb%C3%A9-del-rey-de-hockey-69855069cad2c6f86d0cf93d-g1uv6h0hez?playTime=1",
  "683fb9018a69c5290b08fffb": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-s%C3%AD-a-primera-vista-683fb9018a69c5290b08fffb-b0fxsgx8gm?playTime=1",
  "67651cd50abc6601eb05f198": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-casados-a-primera-vista-67651cd50abc6601eb05f198-m8mfjkgyi9?playTime=1",
  "68e866f6366b9db8a80a85ac": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-atrapada-en-el-abrazo-del-jefe-68e866f6366b9db8a80a85ac-blhmkeh0jr?playTime=1",
  "67b70c556351c6c159052082": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-escort-que-conoc%C3%AD-en-par%C3%ADs-67b70c556351c6c159052082-31sgro7pwl?playTime=1",
  "694cd6fb6416cddfe503b603": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-monstruo-en-sus-ojos-694cd6fb6416cddfe503b603-ctc62gbqhc?playTime=1",
  "69cf7c60dbb397869a026e00": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-barro-y-diamantes-69cf7c60dbb397869a026e00-sq7e6mj1h6?playTime=1",
  "69dc949f3fac423586088e0e": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-guardaespaldas-que-domin%C3%B3-su-destino-69dc949f3fac423586088e0e-i7parjwfzi?playTime=1",
  "68f6f7b6794cc55960091d35": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-superpadrino-mi-ex-me-suplica-de-rodillas-68f6f7b6794cc55960091d35-s8q80cuvgy?playTime=1",
  "69ccb30db76447f29807e8b9": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-maestro-oculto-69ccb30db76447f29807e8b9-7dq68hlcax?playTime=1",
  "69eefd82c9e41a3f6c0e854c": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-el-guardi%C3%A1n-invencible-69eefd82c9e41a3f6c0e854c-3khk3wav7x?playTime=1",
  "6a4c92ad1a588877650016fa": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-francotirador-americano-el-ni%C3%B1o-de-las-armas-6a4c92ad1a588877650016fa-abdtpfmur9?playTime=1",
  "67f344092dc8c4880a0c4a0e": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-novia-muda-del-alfa-malo-67f344092dc8c4880a0c4a0e-jiffnlgerd?playTime=1",
  "6a32779157133faae80f1f36": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-reina-del-drag%C3%B3n-el-precio-de-la-traici%C3%B3n-6a32779157133faae80f1f36-y4mhijjgim?playTime=1",
  "690c0e32f83a46c04400cd73": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-sangre-y-plata-el-ascenso-de-la-pareja-rechazada-del-alfa-690c0e32f83a46c04400cd73-g1ksanulsw?playTime=1",
  "6a3277e71af0b5e5e60294e3": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-la-luna-traicionada-y-el-heredero-perdido-6a3277e71af0b5e5e60294e3-m8p75yrcqu?playTime=1",
  "6a03e54c33c25ace29018ddd": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-luna-rechazada-es-la-reina-del-alfa-6a03e54c33c25ace29018ddd-zyte0kgarl?playTime=1",
  "69dc9d08b756111a550ddf0f": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-te-abrazo-con-el-sol-en-mis-manos-69dc9d08b756111a550ddf0f-51u50dmz56?playTime=1",
  "6853e502879814b6660042a4": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-casados-en-un-instante-y-completamente-malcriados-6853e502879814b6660042a4-hvmgpusue3?playTime=1",
  "6853ec8e75685f58d4007083": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-cayendo-por-mi-esposa-cazafortunas-6853ec8e75685f58d4007083-fxktb4ejhr?playTime=1",
  "6853c0016110016ae1065598": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-libertad-en-la-adversidad-6853c0016110016ae1065598-97g1h5z460?playTime=1",
  "693163d40624b91c7f0244aa": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-destinada-a-los-brazos-del-pr%C3%ADncipe-693163d40624b91c7f0244aa-0ly1q1647z?playTime=1",
  "6a1fdd2fbf438d57240ae0e7": "https://www.reelshort.com/es/episodes/%2Fepisodes%2Fepisode-1-dom%C3%ADname-general-6a1fdd2fbf438d57240ae0e7-m6jmh0tsyo?playTime=1",
};

const capturedMovieUrls = {
  "69d85fe4a95604a7fe07b59f": "https://www.reelshort.com/es/movie/madre-secreta-del-heredero-de-la-mafia-69d85fe4a95604a7fe07b59f",
  "683fb0552ac1937db60b4e32": "https://www.reelshort.com/es/movie/el-sucio-secreto-de-mi-hermanastro-683fb0552ac1937db60b4e32",
  "6a50c6c74053a2c0ee0ff7a3": "https://www.reelshort.com/es/movie/ni%C3%B1era-de-mi-guapo-acosador-6a50c6c74053a2c0ee0ff7a3",
  "6882eb49198f63906e0e07a0": "https://www.reelshort.com/es/movie/verdadera-heredera-vs-falsa-millonaria-6882eb49198f63906e0e07a0",
  "69df6dba827a5e662a0c6849": "https://www.reelshort.com/es/movie/mi-amor-secreto-es-su-hermano-69df6dba827a5e662a0c6849",
  "6a0fd19db6c943fbfc049955": "https://www.reelshort.com/es/movie/el-rey-mendigo-regresa-6a0fd19db6c943fbfc049955",
  "67eb4d2cbfe804cbeb02ba58": "https://www.reelshort.com/es/movie/la-virgen-y-el-millonario-67eb4d2cbfe804cbeb02ba58",
  "6a3df2fabf940cea59003a9b": "https://www.reelshort.com/es/movie/nero-6a3df2fabf940cea59003a9b",
  "693a61ece66552e8f001a1b9": "https://www.reelshort.com/es/movie/francotirador-americano-el-%C3%BAltimo-disparo-693a61ece66552e8f001a1b9",
  "690962af5a3a5909900807cd": "https://www.reelshort.com/es/movie/atada-al-honor-690962af5a3a5909900807cd",
  "6996f682a2ab332ecd096c3d": "https://www.reelshort.com/es/movie/mi-beb%C3%A9-tiene-un-padre-mortal-6996f682a2ab332ecd096c3d",
  "68196a57c421c304cd0e8817": "https://www.reelshort.com/es/movie/renacer-del-amor-y-el-destino-68196a57c421c304cd0e8817",
  "6a5607888e93e894e50ab058": "https://www.reelshort.com/es/movie/mi-mariscal-mi-perdici%C3%B3n-6a5607888e93e894e50ab058",
  "683fb9018a69c5290b08fffb": "https://www.reelshort.com/es/movie/s%C3%AD-a-primera-vista-683fb9018a69c5290b08fffb",
  "684fb89e1a8723c71a0deddf": "https://www.reelshort.com/es/movie/mi-esposa-xxl-684fb89e1a8723c71a0deddf",
  "69893d915afb4283f40e4c3f": "https://www.reelshort.com/es/movie/ya-basta-de-ser-amable-69893d915afb4283f40e4c3f",
  "69dc9d08b756111a550ddf0f": "https://www.reelshort.com/es/movie/te-abrazo-con-el-sol-en-mis-manos-69dc9d08b756111a550ddf0f",
  "6a4f1b867798749acb0ce014": "https://www.reelshort.com/es/movie/dulce-tentaci%C3%B3n-6a4f1b867798749acb0ce014",
  "6a5090431eec2a693b0662c6": "https://www.reelshort.com/es/movie/mi-relaci%C3%B3n-falsa-con-el-amigo-de-mi-ex-6a5090431eec2a693b0662c6",
  "69def6cade5b273ead0509bb": "https://www.reelshort.com/es/movie/la-reina-que-huy%C3%B3-del-rey-lobo-69def6cade5b273ead0509bb",
  "69df6db3827a5e662a0c6839": "https://www.reelshort.com/es/movie/tu-esposo-es-m%C3%ADo-69df6db3827a5e662a0c6839",
};

const heroSlides = [
  {
    title: "Sin querer, envié mensajes hot a mi enemigo",
    image: "/assets/hero/7fbbb560-840f-11f1-8fc1-67160e4754e3.jpg",
  },
  {
    title: "Apártense, llegó el magnate",
    image: "/assets/hero/95053b80-840f-11f1-8fc1-67160e4754e3.jpg",
    href: capturedEpisodeUrls["69def17ad64c48cfe60c8615"],
  },
  {
    title: "La reina del dragón: el precio de la traición",
    image: "/assets/hero/a9809c30-840f-11f1-8fc1-67160e4754e3.jpg",
  },
  {
    title: "Rechazo a 5 Alfas",
    image: "/assets/hero/bf002670-840f-11f1-8fc1-67160e4754e3.jpg",
  },
  {
    title: "La CEO y El Padre Secreto De Su Hija",
    image: "/assets/hero/3fe687c0-7060-11f1-a475-8b2e43cf329c.jpg",
  },
  {
    title: "Waterboy: Segunda oportunidad",
    image: "/assets/hero/d4199be0-840f-11f1-8fc1-67160e4754e3.jpg",
    href: capturedEpisodeUrls["6a291fc053df79f38804054d"],
  },
  {
    title: "Dinero, Armas y Feliz Navidad",
    image: "/assets/hero/3d747be0-8420-11f1-8fc1-67160e4754e3.jpg",
  },
  {
    title: "Novias entre las llamas",
    image: "/assets/hero/eeb6f6a0-840f-11f1-8fc1-67160e4754e3.jpg",
  },
];

const shelves = [
  {
    title: "Nuevos Lanzamientos",
    id: 51000879,
    items: [
      ["¡Papá, soy tu estrella de la suerte!", "/assets/media/7062e05d-06e7-412c-95ed-83bed334b7d4.jpg", "6a50cb594a37b7e5ea0c0c76"],
      ["La esposa falsa del multimillonario", "/assets/media/381cdd94-6bce-4aa9-815b-102b413dde97.jpg", "6a574266f3666a49a80f1eaa"],
      ["Hermandad de mentiras: juramento de venganza", "/assets/media/ebcee0cd-3cc0-4ceb-b58d-65dab250db49.jpg", "6a57383d6238eeb3740747b8"],
      ["Dulce tentación", "/assets/media/5572d13d-9ffa-460b-844d-c69181a33ebd.jpg", "6a4f1b867798749acb0ce014"],
      ["Amor en las cenizas de lo nuestro", "/assets/media/0147bf0b-c313-4f20-b983-afd4f5010a58.jpg", "6a50c9304ca0f84fb700933d", "Doblado"],
      ["La hija de Zeus", "/assets/media/ff305d65-6d9f-4a3b-8724-4149f855db66.jpg", "6a50c3945f279ed277001990", "Doblado"],
      ["Niñera de mi guapo acosador", "/assets/media/5bad27a1-ebd7-41d1-947e-530360a65a30.jpg", "6a50c6c74053a2c0ee0ff7a3", "Doblado"],
    ],
  },
  {
    title: "CLASIFICACIÓN",
    id: 51000880,
    ranking: true,
    items: [
      ["No es la novia que él quería", "/assets/media/056b79b8-b98d-493d-a561-fd86a01a66c4.jpg", "6a3e412b58a5eabbce082cd2", "Doblado"],
      ["El genio de la lámpara bajo contrato", "/assets/media/6ce98955-d773-4799-afd2-af371ca6b71d.jpg", "6a3e3fe2e6b933aba2070614", "Doblado"],
      ["El despertar del Abismo", "/assets/media/03448050-33ee-11f1-acb2-c14bef828c82.jpg", "69be36e15fa05aa0a5090d3f"],
      ["Cuenta regresiva por la vida: rescate a 30.000 pies", "/assets/media/6cd3442e-aa34-40bc-a332-218797058aba.jpg", "68f6f7c5794cc55960091d71"],
      ["El capitán de hockey que me odia", "/assets/media/a0d6fe53-3ff2-47e7-9138-98fb6488ea12.jpg", "6a291f9b53df79f3880404bd", "Doblado"],
      ["Escándalo en el probador", "/assets/media/95e10180-3a4d-11f1-acb2-c14bef828c82.jpg", "69dc921b1015a88977031807"],
      ["Su hermano perdido en el espacio", "/assets/media/23b67517-1792-448d-9c3a-def6d29c5170.jpg", "69b7d5c40c8c1196c0003b54", "Doblado"],
    ],
  },
  {
    title: "Serie Doblada 🎙",
    id: 51000881,
    items: [
      ["No es la novia que él quería", "/assets/media/056b79b8-b98d-493d-a561-fd86a01a66c4.jpg", "6a3e412b58a5eabbce082cd2", "Tendencias"],
      ["El genio de la lámpara bajo contrato", "/assets/media/6ce98955-d773-4799-afd2-af371ca6b71d.jpg", "6a3e3fe2e6b933aba2070614", "Tendencias"],
      ["El capitán de hockey que me odia", "/assets/media/a0d6fe53-3ff2-47e7-9138-98fb6488ea12.jpg", "6a291f9b53df79f3880404bd", "Tendencias"],
      ["Su hermano perdido en el espacio", "/assets/media/23b67517-1792-448d-9c3a-def6d29c5170.jpg", "69b7d5c40c8c1196c0003b54"],
      ["¡Shhh, Profesor! Por Favor, No lo Digas", "/assets/media/efb68990-3518-11f0-b65a-27549cd2a91e.jpg", "68357a414a236167a9025c32"],
      ["Waterboy: Segunda oportunidad", "/assets/media/70bc3a56-356b-4393-ab4f-899d7af4a7a3.jpg", "6a291fc053df79f38804054d"],
      ["La consentida de los tres magnates", "/assets/media/e9fa0090-f782-11f0-84ad-6b5693b490dc.jpg", "69859804c95814e19b0ad4a8"],
    ],
  },
  {
    title: "Identidad Oculta 🎭",
    id: 51000882,
    items: [
      ["El despertar del Abismo", "/assets/media/03448050-33ee-11f1-acb2-c14bef828c82.jpg", "69be36e15fa05aa0a5090d3f"],
      ["Cuenta regresiva por la vida: rescate a 30.000 pies", "/assets/media/6cd3442e-aa34-40bc-a332-218797058aba.jpg", "68f6f7c5794cc55960091d71"],
      ["Apártense, llegó el magnate", "/assets/media/cfbaf7b0-1f5d-47da-b475-9db1737c04fc.jpg", "69def17ad64c48cfe60c8615", "Tendencias"],
      ["El aguador", "/assets/media/8d4f51d4-7107-4a12-bb0a-18a9613ed033.jpg", "694cd7715f7166c5760b6c2d"],
      ["El rey guardián discreto", "/assets/media/c8b31b5d-5d2a-4e34-971b-234590308a93.jpg", "69421d38a16cee9b6f0db474"],
      ["Nunca te divorcies de una Heredera Multimillonaria Secreta", "/assets/media/3c2bbddc45599354.jpg", "64828858d5f75b406b6357d8"],
      ["La Reina CEO: La Venganza De Una Madre", "/assets/media/aa194682-01e0-46c6-846b-fdc5051998fa.jpg", "6836b7ce5bff06fba908bd20"],
    ],
  },
  {
    title: "Relación Tabú",
    id: 51000883,
    items: [
      ["Lo que el viento se llevó", "/assets/media/e2d77440-e49b-11f0-84ad-6b5693b490dc.jpg", "694a2ca1adfd9f446d026951"],
      ["¡Uy! Estoy Enamorada de mi Hermanastro", "/assets/media/fb4342c0-cf2a-11ef-9487-233a2ec55662.jpg", "677e28b639d7346eda0aebfc"],
      ["Fingiendo inocencia, conquistando su corazón", "/assets/media/a9c1b850-13cb-11f1-84ad-6b5693b490dc.jpg", "699fa82c6e46de4a5b09edc8"],
      ["Papi Alfa, hazme tuya", "/assets/media/d792c1d2-c03f-4bd3-bd3b-0c60e4c5a7b8.jpg", "6a1fbe4b23381626270c684c"],
      ["Enamorándome de mi hermanastro, mi enemigo", "/assets/media/9c01e449-d015-4339-815d-8cf87af6ed75.jpg", "6a0ad7fd9d2e9a432f0331ed"],
      ["¡¿Me Enamoré del Mejor Amigo de Mi Hermano?!", "/assets/media/4003d075-d99b-4f51-8831-5cfb086e2570.jpg", "681d6b63ac0e0dc6070023d8"],
      ["La virgen y el millonario", "/assets/media/debcf710-1c76-11f0-a650-71056cbfe3ac.jpg", "67eb4d2cbfe804cbeb02ba58", "Popular"],
    ],
  },
  {
    title: "Bebés y Embarazos 🍼",
    id: 51000884,
    items: [
      ["Una noche con el general del Imperio", "/assets/media/6b83e721-ce5f-4e4f-b266-17f476588cb3.jpg", "6a2779b6436fd9cc500e90ca"],
      ["Estoy Embarazada, ¡Separemonos!", "/assets/media/715a20d0-f4fd-11ef-a38f-0d66b56fc320.jpg", "67bc1a9c2e3827da9c0c0b02"],
      ["La ternura cruel del jefe mafioso", "/assets/media/b8f18d90-3a32-11f1-acb2-c14bef828c82.jpg", "69de16fcea1c6793640283a9"],
      ["Accidentalmente embarazada del Alfa", "/assets/media/b5628fe0-7e34-11f0-a06b-bdb674869ea1.jpg", "6882eb265b6d9601ab098cbc", "Popular"],
      ["Después del divorcio, soy consentida por tres hermanos", "/assets/media/1e9cd738-78b5-46f9-9a16-fb9f6086c52f.jpg", "69c49971e92f4783e60e3a19"],
      ["Su Único Amor", "/assets/media/646173d0-9754-11ef-a2d6-41216ff1602c.jpg", "671b0b5a4c2513f2b1097c8c"],
      ["Mi bebé del rey de hockey", "/assets/media/5302be9f-057d-4dce-8990-c207b31c2ec1.jpg", "69855069cad2c6f86d0cf93d"],
    ],
  },
  {
    title: "Amor a Primera Vista 👄",
    id: 51000885,
    items: [
      ["Sí a primera vista", "/assets/media/de1c7ec0-427d-11f0-b65a-27549cd2a91e.jpg", "683fb9018a69c5290b08fffb", "Popular"],
      ["Casados a Primera Vista", "/assets/media/920fa980-beb6-11ef-a2d6-41216ff1602c.jpg", "67651cd50abc6601eb05f198"],
      ["Atrapada en el abrazo del jefe", "/assets/media/b9ff435d-cd5c-4893-aa8f-427beda11928.jpg", "68e866f6366b9db8a80a85ac"],
      ["La ternura cruel del jefe mafioso", "/assets/media/b8f18d90-3a32-11f1-acb2-c14bef828c82.jpg", "69de16fcea1c6793640283a9"],
      ["El Escort que Conocí en París", "/assets/media/ea1d5de0-f4f6-11ef-a38f-0d66b56fc320.jpg", "67b70c556351c6c159052082", "LATINO"],
      ["Monstruo en sus ojos", "/assets/media/ca669322-ce86-4a23-bade-3516f8044508.jpg", "694cd6fb6416cddfe503b603"],
      ["Mi bebé del rey de hockey", "/assets/media/5302be9f-057d-4dce-8990-c207b31c2ec1.jpg", "69855069cad2c6f86d0cf93d"],
    ],
  },
  {
    title: "Género Masculino",
    id: 51000886,
    items: [
      ["Cuenta regresiva por la vida: rescate a 30.000 pies", "/assets/media/6cd3442e-aa34-40bc-a332-218797058aba.jpg", "68f6f7c5794cc55960091d71"],
      ["Barro y diamantes", "/assets/media/b8a3feb0-326f-11f1-acb2-c14bef828c82.jpg", "69cf7c60dbb397869a026e00"],
      ["El guardaespaldas que dominó su destino", "/assets/media/f82ed820-3981-11f1-acb2-c14bef828c82.jpg", "69dc949f3fac423586088e0e"],
      ["Superpadrino: mi ex me suplica de rodillas", "/assets/media/72dcf0df-8150-4069-9e31-5b4b16ab62f9.jpg", "68f6f7b6794cc55960091d35"],
      ["El maestro oculto", "/assets/media/0986fe40-2f5a-11f1-acb2-c14bef828c82.jpg", "69ccb30db76447f29807e8b9"],
      ["El guardián invencible", "/assets/media/e1c825f0-43b8-11f1-acb2-c14bef828c82.jpg", "69eefd82c9e41a3f6c0e854c"],
      ["Francotirador americano: el niño de las armas", "/assets/media/78b5c5e7-6688-46e4-978b-243e4930826e.jpg", "6a4c92ad1a588877650016fa"],
    ],
  },
  {
    title: "Hombre Lobo 🐺y Vampiro🧛",
    id: 51000887,
    items: [
      ["La novia muda del Alfa malo", "/assets/media/f55dc4c5-3289-481b-aaf8-780f2d9a7327.jpg", "67f344092dc8c4880a0c4a0e"],
      ["La reina del dragón: el precio de la traición", "/assets/media/3b0b701d-c01d-4b29-a707-2a7dc0699e00.jpg", "6a32779157133faae80f1f36", "Popular"],
      ["Accidentalmente embarazada del Alfa", "/assets/media/b5628fe0-7e34-11f0-a06b-bdb674869ea1.jpg", "6882eb265b6d9601ab098cbc", "Popular"],
      ["Sangre y plata: el ascenso de la pareja rechazada del Alfa", "/assets/media/4b16f5ff-5b9c-42cd-a326-97ada85bf494.jpg", "690c0e32f83a46c04400cd73"],
      ["La luna traicionada y el heredero perdido", "/assets/media/2c62764b-c444-4055-a743-15d49d62e2d1.jpg", "6a3277e71af0b5e5e60294e3"],
      ["Papi Alfa, hazme tuya", "/assets/media/d792c1d2-c03f-4bd3-bd3b-0c60e4c5a7b8.jpg", "6a1fbe4b23381626270c684c"],
      ["Luna rechazada es la reina del Alfa", "/assets/media/1131ff22-c827-4f92-9b4c-54d9e913e0e4.jpg", "6a03e54c33c25ace29018ddd"],
    ],
  },
  {
    title: "Historias de Asia 🌏",
    id: 51000888,
    items: [
      ["Te abrazo con el sol en mis manos", "/assets/media/597bf2c0-3333-11f1-acb2-c14bef828c82.jpg", "69dc9d08b756111a550ddf0f"],
      ["La consentida de los tres magnates", "/assets/media/e9fa0090-f782-11f0-84ad-6b5693b490dc.jpg", "69859804c95814e19b0ad4a8", "Doblado"],
      ["Casados en un Instante y Completamente Malcriados", "/assets/media/617e18a0-49a5-11ef-a96f-c3bf05c2bf9d.jpg", "6853e502879814b6660042a4", "Doblado"],
      ["Cayendo por Mi Esposa Cazafortunas", "/assets/media/d34eae10-711b-11f0-a06b-bdb674869ea1.jpg", "6853ec8e75685f58d4007083", "Doblado"],
      ["Libertad en la Adversidad", "/assets/media/c428a550-46ad-11f0-860b-97fc2eb1c6d9.jpg", "6853c0016110016ae1065598"],
      ["Destinada a los brazos del príncipe", "/assets/media/1f14b790-cab8-11f0-84ad-6b5693b490dc.jpg", "693163d40624b91c7f0244aa"],
      ["Domíname, general", "/assets/media/ff7e46ae-de4c-4c96-a575-85aad5440fee.jpg", "6a1fdd2fbf438d57240ae0e7"],
    ],
  },
  {
    title: "Más Recomendados",
    id: 51000889,
    recommended: true,
    items: [
      ["Madre Secreta del Heredero de la Mafia", "/assets/media/e58b8330-443f-11f1-acb2-c14bef828c82.jpg", "69d85fe4a95604a7fe07b59f"],
      ["El Sucio Secreto de mi Hermanastro", "/assets/media/aceff1a0-37c0-11f0-b65a-27549cd2a91e.jpg", "683fb0552ac1937db60b4e32", "Doblado"],
      ["Niñera de mi guapo acosador", "/assets/media/5bad27a1-ebd7-41d1-947e-530360a65a30.jpg", "6a50c6c74053a2c0ee0ff7a3"],
      ["Verdadera heredera vs Falsa millonaria", "/assets/media/93fdac30-83da-11f0-a06b-bdb674869ea1.jpg", "6882eb49198f63906e0e07a0"],
      ["Mi amor secreto es su hermano", "/assets/media/9e347323-e076-4cda-a3b8-40eb64d6955f.jpg", "69df6dba827a5e662a0c6849", "Doblado"],
      ["El rey mendigo regresa", "/assets/media/a7913a1a-abe4-4d82-9b0d-7dd44d087b40.jpg", "6a0fd19db6c943fbfc049955", "Doblado"],
      ["La virgen y el millonario", "/assets/media/debcf710-1c76-11f0-a650-71056cbfe3ac.jpg", "67eb4d2cbfe804cbeb02ba58"],
      ["NERO", "/assets/media/06e89582-25db-47ec-b4a6-061e0d12ad5c.jpg", "6a3df2fabf940cea59003a9b"],
      ["Francotirador americano: el último disparo", "/assets/media/43e2de60-d5af-11f0-84ad-6b5693b490dc.jpg", "693a61ece66552e8f001a1b9", "Doblado"],
      ["Atada al honor", "/assets/media/4e908a85-ff87-49a3-a477-f77091a521f8.jpg", "690962af5a3a5909900807cd"],
      ["Mi bebé tiene un padre mortal", "/assets/media/171693f0-fc0f-11f0-84ad-6b5693b490dc.jpg", "6996f682a2ab332ecd096c3d", "Doblado"],
      ["Renacer del Amor y el Destino", "/assets/media/3bb43b20-0f90-11f0-a38f-0d66b56fc320.jpg", "68196a57c421c304cd0e8817", "Doblado"],
      ["Mi mariscal, mi perdición", "/assets/media/2673a922-a5a8-4bb0-9ca9-f15536767f49.jpg", "6a5607888e93e894e50ab058"],
      ["Sí a primera vista", "/assets/media/de1c7ec0-427d-11f0-b65a-27549cd2a91e.jpg", "683fb9018a69c5290b08fffb"],
      ["Mi Esposa XXL", "/assets/media/cd2e8ad0-3cfc-11f0-b65a-27549cd2a91e.jpg", "684fb89e1a8723c71a0deddf", "Doblado"],
      ["Ya basta de ser amable", "/assets/media/22fd69a0-fb6f-11f0-84ad-6b5693b490dc.jpg", "69893d915afb4283f40e4c3f", "Doblado"],
      ["Te abrazo con el sol en mis manos", "/assets/media/597bf2c0-3333-11f1-acb2-c14bef828c82.jpg", "69dc9d08b756111a550ddf0f", "Doblado"],
      ["Dulce tentación", "/assets/media/5572d13d-9ffa-460b-844d-c69181a33ebd.jpg", "6a4f1b867798749acb0ce014"],
      ["Mi relación falsa con el amigo de mi ex", "/assets/media/69c100f8-15f5-4b75-9647-df305ee61499.jpg", "6a5090431eec2a693b0662c6"],
      ["La reina que huyó del rey lobo", "/assets/media/c0d9a6ba-9e14-49f9-ab66-b459969a9b47.jpg", "69def6cade5b273ead0509bb"],
      ["Tu esposo es mío", "/assets/media/94041a7d-5256-4c28-8c37-8a2cce5eba64.jpg", "69df6db3827a5e662a0c6839", "Doblado"],
    ],
  },
];

function capturedItemUrl(id, recommended) {
  return recommended ? capturedMovieUrls[id] : capturedEpisodeUrls[id];
}

function capturedShelfUrl(id) {
  return capturedShelfUrls[id];
}

function Icon({ children, label }) {
  return (
    <span aria-hidden="true" className="nav-icon" title={label}>
      {children}
    </span>
  );
}

function LanguageNotice({ onClose }) {
  return (
    <div className="language-notice" data-pwc-section="language-notice">
      <span>
        Perhaps you would like to switch to{" "}
        <a href="https://www.reelshort.com/">English</a>
        <span className="notice-chevron">›</span>
      </span>
      <button type="button" aria-label="Cerrar aviso" onClick={onClose}>
        ×
      </button>
    </div>
  );
}

function Header({ downloadOpen, onDownloadToggle }) {
  const [localeOpen, setLocaleOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header
      className="site-header"
      data-pwc-section="header"
      data-pwc-critical="header-1"
    >
      <nav className="nav-shell" aria-label="Navegación principal">
        <a className="brand" href="https://www.reelshort.com/es" aria-label="ReelShort">
          <img
            className="brand-mark"
            src="/assets/media/211d3420-d721-11f0-84ad-6b5693b490dc.png"
            alt=""
          />
          <img
            className="brand-name"
            src="/assets/media/8f9e3f90-5a37-11f1-b0e9-f1e04973cf14.png"
            alt="ReelShort"
          />
        </a>
        <div className="primary-links">
          <a className="active" href="https://www.reelshort.com/es">Inicio</a>
          <a href="https://www.reelshort.com/es/genre">Categorías</a>
          <a href="https://www.reelshort.com/es/fandom">Club de<br />fans</a>
          <a href="https://www.reelshort.com/es">Marca</a>
        </div>
        <div className="utility-links">
          <a href="https://www.reelshort.com/es/search" aria-label="Buscar">
            <Icon label="Buscar">
              <svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="7.5" /><path d="m16 16 5 5" /></svg>
            </Icon>
            <span>Buscar</span>
          </a>
          <button
            className="utility-button"
            type="button"
            data-pwc-interaction="interaction-2"
            aria-label="Descargar ReelShort"
            aria-controls="download-menu"
            aria-expanded={downloadOpen}
            onClick={onDownloadToggle}
          >
            <Icon label="Descargar">
              <svg viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="2" /><path d="M10 5h4M10 19h4" /></svg>
            </Icon>
            <span>Descargar</span>
          </button>
          <a href="https://www.reelshort.com/es/dashboard" aria-label="Historial">
            <Icon label="Historial">
              <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 6v6l4 2" /></svg>
            </Icon>
            <span>Historial</span>
          </a>
          <button
            className="locale utility-button"
            type="button"
            aria-label="Cambiar idioma: Español"
            aria-controls="locale-menu"
            aria-expanded={localeOpen}
            onClick={() => setLocaleOpen((open) => !open)}
          >
            <Icon label="Idioma">
              <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" /><path d="M2 12h20M12 2c3 3 4 6 4 10s-1 7-4 10c-3-3-4-6-4-10s1-7 4-10" /></svg>
            </Icon>
            <span>Español⌄</span>
          </button>
          <a className="avatar" href="https://www.reelshort.com/es/dashboard" aria-label="Perfil">
            <span />
          </a>
          <button
            className="mobile-menu-toggle"
            type="button"
            aria-label="Abrir menú"
            aria-controls="mobile-menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((open) => !open)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
        {localeOpen && (
          <div className="locale-menu" id="locale-menu" role="menu">
            <a role="menuitem" href="https://www.reelshort.com/">English</a>
            <button role="menuitem" type="button" onClick={() => setLocaleOpen(false)}>
              Español ✓
            </button>
          </div>
        )}
        {mobileOpen && (
          <div className="mobile-menu" id="mobile-menu">
            <a className="active" href="https://www.reelshort.com/es">Inicio</a>
            <a href="https://www.reelshort.com/es/genre">Categorías</a>
            <a href="https://www.reelshort.com/es/fandom">Club de fans</a>
            <button type="button" onClick={onDownloadToggle}>Descargar</button>
          </div>
        )}
      </nav>
    </header>
  );
}

function HeroCarousel() {
  const [activeSlide, setActiveSlide] = useState(1);
  const slide = heroSlides[activeSlide];

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveSlide((current) => (current + 1) % heroSlides.length);
    }, 6000);
    return () => window.clearInterval(timer);
  }, []);

  const selectRelative = (offset) => {
    setActiveSlide((current) => (
      (current + offset + heroSlides.length) % heroSlides.length
    ));
  };

  return (
    <section
      className="hero-carousel"
      data-pwc-critical="hero-1"
      aria-roledescription="carousel"
      aria-label="Historias destacadas"
    >
      {heroSlides.map((item, index) => (
        <img
          key={item.image}
          className={`hero-image${index === activeSlide ? " active" : ""}`}
          src={item.image}
          alt=""
          aria-hidden={index !== activeSlide}
          loading={index < 2 ? "eager" : "lazy"}
          fetchPriority={index === 1 ? "high" : "auto"}
        />
      ))}
      <div className="hero-shade" />
      <button
        className="hero-arrow hero-arrow-left"
        type="button"
        aria-label="Historia anterior"
        onClick={() => selectRelative(-1)}
      >
        ‹
      </button>
      <button
        className="hero-arrow hero-arrow-right"
        type="button"
        aria-label="Historia siguiente"
        onClick={() => selectRelative(1)}
      >
        ›
      </button>
      <div className="hero-copy" aria-live="polite">
        <h1>{slide.title}</h1>
        {slide.href ? (
          <a className="hero-play" href={slide.href}>
            <span aria-hidden="true">▶</span> Reproducir
          </a>
        ) : (
          <button className="hero-play" type="button">
            <span aria-hidden="true">▶</span> Reproducir
          </button>
        )}
      </div>
      <div className="hero-dots" role="tablist" aria-label="Elegir historia">
        {heroSlides.map((item, index) => (
          <button
            key={item.image}
            type="button"
            role="tab"
            {...(index === 0
              ? { "data-pwc-interaction": "interaction-1" }
              : {})}
            aria-label={`Mostrar ${item.title}`}
            aria-selected={index === activeSlide}
            className={index === activeSlide ? "active" : ""}
            onClick={() => setActiveSlide(index)}
          />
        ))}
      </div>
    </section>
  );
}

function PosterCard({ item, rank, recommended, eager = false }) {
  const [title, image, id, badge] = item;
  const displayTitle = recommended ? `${title} Serie completa` : title;
  return (
    <a className="poster-card" href={capturedItemUrl(id, recommended)}>
      <span className="poster-frame">
        <img
          src={image}
          alt={displayTitle}
          loading={eager ? "eager" : "lazy"}
          fetchPriority={eager ? "high" : "auto"}
        />
        {badge && (
          <span className={`badge badge-${badge.toLocaleLowerCase("es")}`}>
            {badge}
          </span>
        )}
        {rank && <strong className="rank">{rank}</strong>}
      </span>
      <span className="poster-title">{displayTitle}</span>
    </a>
  );
}

function Shelf({ shelf, shelfIndex }) {
  return (
    <section
      className={`shelf${shelf.recommended ? " recommended" : ""}`}
      data-pwc-shelf={shelf.id}
    >
      <div className="shelf-heading">
        <h2>
          {shelf.recommended ? (
            shelf.title
          ) : (
            <a href={capturedShelfUrl(shelf.id)}>{shelf.title}</a>
          )}
        </h2>
        {!shelf.recommended && (
          <a className="view-all" href={capturedShelfUrl(shelf.id)}>
            Ver todo <span>›</span>
          </a>
        )}
      </div>
      <div className="poster-grid">
        {shelf.items.map((item, index) => (
          <PosterCard
            key={`${shelf.id}-${item[2]}`}
            item={item}
            rank={shelf.ranking ? index + 1 : null}
            recommended={shelf.recommended}
            eager={shelfIndex === 0}
          />
        ))}
      </div>
    </section>
  );
}

function FauxQr() {
  return (
    <div className="qr" role="img" aria-label="Código QR para descargar ReelShort">
      <i className="finder finder-one" />
      <i className="finder finder-two" />
      <i className="finder finder-three" />
      <b>R</b>
    </div>
  );
}

function Footer() {
  return (
    <footer
      className="site-footer"
      data-pwc-section="footer"
      data-pwc-critical="footer-1"
    >
      <div className="footer-main">
        <div className="footer-brand">
          <img
            src="/assets/media/8f9e3f90-5a37-11f1-b0e9-f1e04973cf14.png"
            alt="ReelShort"
          />
          <p>© 2026 Crazy Maple Studio™, Inc. Todos los derechos reservados.</p>
          <div className="socials" aria-label="Redes sociales">
            <a href="https://www.facebook.com/ReelShortTV/" aria-label="Facebook">f</a>
            <a href="https://www.youtube.com/@reelshortapp" aria-label="YouTube">▶</a>
            <a href="https://www.instagram.com/reelshortapp/" aria-label="Instagram">◎</a>
            <a href="https://www.tiktok.com/@reelshortapp" aria-label="TikTok">♪</a>
          </div>
        </div>
        <div className="footer-column">
          <h3>SOBRE</h3>
          <a href="https://www.reelshort.com/youtube-api-terms.html">Condiciones de Servicio</a>
          <a href="https://www.reelshort.com/youtube-api-privacy.html">Política de Privacidad</a>
          <a href="mailto:reelshort.support@crazymaplestudio.com">Contáctenos</a>
          <small>Horas de Servicio: Lunes a Domingo, de 12 a.m. a 8 a.m. (Hora del Este)</small>
        </div>
        <div className="footer-column support">
          <h3>SOPORTE</h3>
          <span>Comentarios</span>
          <a href="mailto:rachelbencosme@crazymaplestudio.com">Medios y Relaciones<br />Públicas</a>
        </div>
        <div className="download-column">
          <h3>Descargar</h3>
          <FauxQr />
          <p>Desbloquea episodios<br />gratis solo en la app</p>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  const [noticeOpen, setNoticeOpen] = useState(true);
  const [downloadOpen, setDownloadOpen] = useState(false);

  return (
    <div className="page">
      {noticeOpen && <LanguageNotice onClose={() => setNoticeOpen(false)} />}
      <Header
        downloadOpen={downloadOpen}
        onDownloadToggle={() => setDownloadOpen((open) => !open)}
      />
      <HeroCarousel />
      <main data-pwc-section="section">
        {shelves.map((shelf, shelfIndex) => (
          <Shelf key={shelf.id} shelf={shelf} shelfIndex={shelfIndex} />
        ))}
        <p className="end-note">Has desplazado hasta el fondo</p>
      </main>
      <Footer />
      {downloadOpen && (
        <aside className="download-menu" id="download-menu" aria-label="Descargar ReelShort">
          <button
            className="download-menu-close"
            type="button"
            aria-label="Cerrar descarga"
            onClick={() => setDownloadOpen(false)}
          >
            ×
          </button>
          <h3>Descargar</h3>
          <FauxQr />
          <p>Desbloquea episodios<br />gratis solo en la app</p>
        </aside>
      )}
      <button
        className="download-fab"
        type="button"
        aria-label="Descargar"
        aria-controls="download-menu"
        aria-expanded={downloadOpen}
        onClick={() => setDownloadOpen((open) => !open)}
      >
        ⇩
      </button>
    </div>
  );
}
