# TODO — Links de Afiliados Pendientes

Cuando tengas los links de afiliados, pégalos en `scripts/afiliados.json` y haz push
(o pídele a Claude Code que lo haga).

## Cómo actualizar un link

1. Abre `scripts/afiliados.json`
2. Busca el bloque del afiliado (ej: `"kit"`)
3. Reemplaza `https://AFILIADO-PENDIENTE/kit` por tu link real de afiliado
4. Guarda el archivo y haz push: `git add scripts/afiliados.json && git commit -m "afiliados: agregar link kit" && git push`

## Estado de registros

| Marcador | Herramienta | Link real | Estado |
|---|---|---|---|
| `kit` | Kit (ex-ConvertKit) | — | ⏳ Pendiente — Registrarse en kit.com/affiliate |
| `writesonic` | Writesonic | — | ⏳ Pendiente — writesonic.com (programa de afiliados) |
| `frase` | Frase | — | ⏳ Pendiente — frase.io/affiliate |
| `jasper` | Jasper | — | ⏳ Pendiente — jasper.ai (partner program) |
| `headshotpro` | HeadshotPro | — | ⏳ Pendiente — headshotpro.com (Rewardful) |
| `photoai` | PhotoAI | — | ⏳ Pendiente — photoai.com (afiliados) |
| `synthesia` | Synthesia | — | ⏳ Pendiente — synthesia.io (partner program) |
| `beehiiv` | beehiiv | — | ⏳ Pendiente — beehiiv.com/affiliates |

## Prioridad de registro

Empieza por estos dos (los que más artículos van a referenciar):
1. **Kit** — kit.com/affiliate (50% recurrente por 12 meses)
2. **Writesonic** — writesonic.com (~30% recurrente)

## Dominio propio (recomendado)

Conectar un dominio propio (~USD 10/año) en Vercel mejora significativamente el SEO.
Se hace desde: Dashboard Vercel → proyecto inmoia → Settings → Domains.
