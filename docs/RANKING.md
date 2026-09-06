# Ranking

## Integração

`core/leaderboard_client.py` acessa diretamente a API REST do Supabase. Não há
servidor intermediário. A aba `ui/leaderboard_tab.py` envia os melhores tempos
MoTeC e mostra o melhor resultado por piloto, carro e pista.

O ranking usa uma tabela `leaderboard` com histórico insert-only. As políticas
RLS documentadas no README permitem `insert` e `select` para a chave pública
`anon`; não há update/delete público configurado pelo projeto.

## Configuração

Defina `SUPABASE_URL` e `SUPABASE_KEY` no `.env`. Use somente a chave
`anon public`; nunca use `service_role` em um cliente distribuído.

Se as chaves estiverem vazias, o aplicativo continua funcionando e apenas o
ranking compartilhado fica desabilitado. O Discord pode notificar novos
recordes quando `DISCORD_WEBHOOK_URL` estiver configurado.

## Contribuindo

Não inclua URL, chave, payload ou screenshot reais. Testes de rede devem usar
um projeto descartável e não devem ser executados automaticamente em CI.
Mudanças no schema precisam atualizar o SQL do README e esta documentação.
