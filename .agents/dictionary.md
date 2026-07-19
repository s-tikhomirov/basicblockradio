# Transcript Editing Dictionary

Proper spellings for technical terms, project names, and non-trivial vocabulary in podcast transcripts.

---

## Spelled in English

### Protocols and Platforms
- 1inch
- a16z
- AAVE
- Aave
- Acki Nacki
- Amper Computing
- Arbitrum
- Binance
- BitFury
- Boosty
- Chainlink
- Citrea
- Celestia
- Sophon
- Cloudflare
- Coinbase
- Cursor
- CybOS
- Cosmos
- CowSwap
- C.R.E.A.M. Finance
- Curve
- DeFi Llama
- EigenLayer
- Ether.Fi
- Ethereum
- Falcon
- Fluence
- Gearbox
- Golem
- Jito
- Kelp
- Kyber
- Lido
- Lovable
- Mainnet
- Maker
- Marinade
- Mellow
- Merkle Tree Certificates
- Messari
- Morpho
- Polkadot
- Pudgy Penguins
- QApp
- Renzo
- Rocket Pool
- Signal
- SLH-DSA
- Solana
- Spark
- SPHINCS
- SPHINCS+
- SHRINCS
- Stakehound
- stETH
- Tezos
- The Block
- Tornado Cash
- WhatsApp
- Zerion
- Cyber.Fund
- LangChain
- LlamaIndex
- Qdrant
- Nous Research
- OneBalance
- Pluralis
- Gensyn
- Prime Intellect
- Pump.fun
- iMessage
- zkSync Era
- ZK Stack
- Shared Bridge
- Caldera
- Zeeve
- Conduit
- QuickNode
- Alchemy
- Solidity
- SolC
- SolX

### Technical Terms
- AML
- API
- APR
- blue chip
- capital efficiency
- collateral
- curated vaults
- DAO
- DeFi
- DePIN
- Dual Governance
- ETF
- HSM
- Harvest Now Decrypt Later
- KPI
- KYC
- NFT
- PKI
- Provable Security
- Rage Quit
- SNARKs
- STARKs
- Web3
- Wi-Fi
- code-based
- delegation
- double-spend
- governance
- hash-based
- isogeny-based
- issuance
- lattice-based
- layer-1
- layer-2
- liquid staking
- market share
- multisig
- post-quantum
- CRQC
- restaking
- side-channel
- slashing
- treasury
- vault
- withdrawal queue
- data availability
- opcode
- precompile
- sequencing
- sequencer
- self-play
- light client
- fraud proof
- proof-of-work
- proof-of-stake
- batch
- paymaster

### People and Organizations

Russian hosts, guests, and researchers who speak Russian on the show: **Cyrillic only** in transcript and readable (no English parenthetical). Examples: `Дмитрий Ховратович`, `Михаил Кудинов`, `Сергей Тихомиров`.

Foreign researchers and guests: **Russian surface forms** in transcript and readable (correct case per line). Canonical Latin spelling from papers lives in `.agents/foreign-persons.json`; readable gets one ` (English Name)` per person per episode via `scripts/disclose_foreign_names.py` (see `transcript-to-readable` skill). Do not put those parentheses in `NNN-transcript.md` (shorts are verbatim from transcript).

- 21Shares
- Dan Boneh
- Eindhoven University
- Ethereum Foundation
- Matter Labs
- Nic Carter
- Justin Drake
- Илья Суцкевер
- Алан Тьюринг
- Lazarus Group
- Leslie Lamport
- NIST
- NSA
- Oracle (в значении компании)
- Patreon
- Russian Quantum Center
- SEC
- Tanja Lange
- WisdomTree

### Foreign persons (readable disclosure)

Machine-readable list: `.agents/foreign-persons.json`. Each entry has `english`, `given`, `family`, and `family_indeclinable` (when true, only the given name takes case endings in Russian, e.g. `с Дэном Боне`). Add new people there when an episode cites them; map ASR noise in Equivalent Terms below to the Russian nominative pair.

---

## Spelled in Russian

### Technical Concepts
- байт
- билдер
- блокчейн
- валидатор
- делегация
- дискретное логарифмирование
- изогении
- коммьюнити
- криптоанализ
- кубиты
- курация
- куратор
- квантовый компьютер
- килобайт
- лендинг
- ликвидность
- ликвидный стейкинг
- минтинг
- нод-оператор
- оракул
- период группы
- рестейкинг
- сайд-проект
- чат-бот
- решетки
- слэшинг
- стейк
- стейкинг
- стратегия
- тим-лид
- факторизация
- форк
- группы
- хакатон
- шифропанк
- юз-кейс
- эллиптические кривые
- он-чейн
- вайбкодить
- Киберфонд

### Common Phrases
- Базовый Блок (podcast name; both words capitalized in all cases: Базового Блока, Базовому Блоку, Базовым Блоком, Базовом Блоке — not «Базовый блок»)
- Виталик
- кофаундер
- проаудированный
- вход рубль, выход два = вход рубль, выход два (idiom for expensive entry/exit)

### Show notes and episode description (приложить / добавить)

When hosts mean they will put a link or reference in show notes or the episode description (YouTube, podcast platforms):

- Prefer приложить when normalizing mistaken wording (especially «предложить ссылку в описании» and similar — see Equivalent Terms).
- If the speaker clearly said добавить (`добавим в описание`, `добавим в шоуноты`, `добавим ссылку в описание`), keep добавить; do not swap to приложить in transcript or readable.
- приложить and добавить in this sense are both fine editorially; choose by what was spoken.

- `приложим ссылку в описании`, `приложим в шоуноты`, `приложим в шоуноты ссылку`, `приложим к шоунотам` — both `в шоуноты` and `к шоунотам` are fine; keep whichever the speaker used
- `описание` / `описании` = episode description field; `шоуноты` = written show notes

---

## Context-Dependent

- vault vs волт: Use "волт" in casual speech, "vault" in technical descriptions
- Cosmos vs космос: Use "Cosmos" for the blockchain protocol, "космос" for literal space/universe. When the speaker says "коммьюнити Космоса" referring to the blockchain ecosystem, use "Cosmos". When they say "в космосе" meaning outer space, use "космос".

---

## Abbreviations

| Short | Full | Notes |
|-------|------|-------|
| stETH | staked ETH | Liquid staking token |
| LDO | Lido DAO Token | Governance token |
| LST | Liquid Staking Token | Generic term for liquid staking tokens |
| EPR | Effective Percentage Rate | Staking yield metric |
| MEV | Maximal Extractable Value | Block production profit |
| KYC | Know Your Customer | Identity verification |
| AML | Anti-Money Laundering | Compliance process |
| DAO | Decentralized Autonomous Organization | Governance structure |
| DeFi | Decentralized Finance | Financial protocols |
| NFT | Non-Fungible Token | Unique digital asset |
| API | Application Programming Interface | Software interface |
| APR | Annual Percentage Rate | Yield metric |
| ETP | Exchange-Traded Product | Financial instrument |
| ETF | Exchange-Traded Fund | Investment fund |
| HSM | Hardware Security Module | Physical device for key storage |
| KPI | Key Performance Indicator | Performance metric |
| PKI | Public Key Infrastructure | Certificate management system |
| SNARK | Succinct Non-interactive Argument of Knowledge | Zero-knowledge proof; plural SNARKs |
| SHRINCS | — | Blockstream hash-based signature combo (stateful + stateless fallback); name from SPHINCS and shrink; not «Shrinks» |
| STARK | Scalable Transparent Argument of Knowledge | Post-quantum zero-knowledge proof |
| CRQC | Cryptographically Relevant Quantum Computer | Квантовый компьютер, релевантный для взлома криптографии; in show notes and transcripts use «CRQC» when context is clearly crypto (threat to PKI, signatures, migration), otherwise «квантовый компьютер» |
| EIP-4337 | Ethereum account abstraction (ERC-4337) | Spoken «EIP-4337», not «4337» or «IP 4337» alone |
| EIP-7702 | Set EOA code for one transaction | Spoken «EIP-7702», not «IP 7702» |
| OP_CAT | Bitcoin opcode (Cat) | Proposed for verifying proofs on Bitcoin; not «OPCAT» |

---

## Equivalent Terms (Alternative Spellings)

Terms that are equivalent and should not be flagged as discrepancies during SRT comparison. Format: `alternative form = canonical form`

- Базовый блок = Базовый Блок
- базовый блок = Базовый Блок
- Базового блока = Базового Блока
- Базовому блоку = Базовому Блоку
- Базовым блоком = Базовым Блоком
- Базовом блоке = Базовом Блоке
- биткоин = Bitcoin (ASR equivalent only; in Russian transcript output use `биткоин` / `биткоины` / `биткоинов` for currency amounts, and `Bitcoin` for network or protocol — see srt-to-transcript skill, Bitcoin vs биткоин)
- биткойн = Bitcoin
- байнэнс = Binance
- бикончейн = beacon chain
- Виталик = Виталик Бутерин
- Vitalik = Виталик
- Pudgey Penguins = Pudgy Penguins
- Citria = Citrea
- OPCAT = OP_CAT
- Миссари = Messari
- дабл спенд = double-spend
- IP 7702 = EIP-7702
- IP 4337 = EIP-4337
- Ник Карткр = Ник Картер
- Джастин Рейком = Джастин Дрейк
- Джастином Рейком = Джастином Дрейком
- Виндикт Вагнер = Бенедикт Вагнер
- Эра = Era
- Эру = Era
- Эры = Era
- Эре = Era
- предложим ссылку в описании = приложим ссылку в описании
- предложим в описании = приложим в описании
- пич = питч
- трансляций в секунду = транзакций в секунду
- волт = vault
- гovernance = governance
- капитал-эффективность = capital efficiency
- дапп = dapp
- ДАО = DAO
- дефи = DeFi
- децентрализованно = decentrally
- депег = depeg
- деплой = deploy
- документация = documentation
- доллар = USD
- интерфейс = interface
- коммьюнити = community
- конфа = конференция
- крипта = криптовалюта
- крипто = криптовалютный
- лендинг = lending
- ликвидность = liquidity
- ликвидный стейкинг = liquid staking
- moat = moat (экономический ров, конкурентное преимущество)
- мейннет = mainnet
- минтинг = minting
- нод-оператор = node operator
- оракул = oracle
- ребейз = rebase
- рестейкинг = restaking
- синтетикс = Synthetix
- слэшинг = slashing
- snark = SNARK
- snarks = SNARKs
- снарки = SNARKs
- Shrinks = SHRINCS
- shrinks = SHRINCS
- byte = байт
- bytes = байт
- Byte = байт
- kilobyte = килобайт
- kilobytes = килобайт
- builder = билдер (Ethereum proof-of-stake block builder; PBS, MEV pipeline)
- builders = билдеры
- use case = юз-кейс
- use cases = юз-кейсы
- use-case = юз-кейс
- смарт-контракт = smart contract
- smart contract = смарт-контракт
- Smart Contract = смарт-контракт
- стейк = stake
- стейкинг = staking
- токен = token
- трейдинг = trading
- вайп кодил = вайбкодил
- вайп кодить = вайбкодить
- вайпкодил = вайбкодил
- вайпкодить = вайбкодить
- киберфонд = Киберфонд
- A16Z = a16z
- AmbitFury = BitFury
- AVI = AAVE
- PumptotFan = Pump.fun
- pump.fun = Pump.fun
- Chatbot = чат-бот
- Co-Swap = CowSwap
- CYBOS = CybOS
- Cybose = CybOS
- One Balance = OneBalance
- лавабл = Lovable
- chatbot = чат-бот
- чатбот = чат-бот
- чатботов = чат-ботов
- сайт-проект = сайд-проект
- сайт-проекта = сайд-проекта
- сайт-проектам = сайд-проектам
- тем лед = тим-лид
- тем леду = тим-лиду
- тем лид = тим-лид
- тем лиду = тим-лиду
- киберфонда = Киберфонда
- киберфонду = Киберфонду
- киберфондов = Киберфонда
- Cyber Fund = Cyber.Fund
- Cyberfund = Cyber.Fund
- Cyber fund = Cyber.Fund
- Line = LangChain
- Leto = LlamaIndex
- Quadrant = Qdrant
- Nus Research = Nous Research
- Jensen = Gensyn
- Илья Sutskever = Илья Суцкевер
- Sutskever = Суцкевер
- Судсковер = Суцкевер
- Суцкий = Суцкевер
- Turing = Тьюринг
- тест Turing = тест Тьюринга
- Turing test = тест Тьюринга
- тестнет = testnet
- холд = hold
- эфир = Ethereum
- эфириум = Ethereum
- АМЛ = AML
- КУС = KYC
- Сатоши = Satoshi
- Сатоша Накамото = Сатоши Накамото
- Сатоша = Сатоши
- кубит = qubit
- решетка = lattice
- изогения = isogeny
- пост-квантовый = post-quantum
- on-чейн = он-чейн
- ончейн = он-чейн
- обкодов = opcode
- обкод = opcode
- прикомпайл = precompile
- прикомпайлы = precompiles
- сиквинсинг = sequencing
- сиквинсингом = sequencing
- сиквенсер = sequencer
- сиквенсера = sequencer
- Matterlapse = Matter Labs
- light-клайент = light client
- light-клайенты = light client
- фрод-пруф = fraud proof
- фрод-пруфа = fraud proof
- фродпруф = fraud proof
- proof of work = proof-of-work
- proof of stake = proof-of-stake
- бачи = batches
- батч = batch
- батчи = batches
- Serg Bridge = Shared Bridge
- Толдера = Caldera
- Изиев = Zeeve
- Алкими = Alchemy
- роллап из-за сервис = rollup-as-a-service
- пеймастер = paymaster
- пеймастера = paymaster
- пеймастерам = paymasters
- Сафон = Sophon
- Сафоном = Sophon
- Сафоне = Sophon
- MatterLabs = Matter Labs
- Ethereum фаундейшн = Ethereum Foundation
- селестией = Celestia
- селестия = Celestia
- л1 = L1
- Л1 = L1
- эсэсол = SolX
- эсэсл = SolC
- эсэсо = ZK Stack

---

## Notes

1. Project names always keep English capitalization: Lido, AAVE, Solana, Cosmos
2. Naturalized terms use Russian spelling: блокчейн, стейкинг, коммьюнити
3. Technical abbreviations stay in English: MEV, KYC, AML, stETH
4. Consistency within a transcript is more important than strict rules
5. During SRT comparison, terms in the Equivalent Terms section are considered identical
6. zkSync rollup product name: use Era (Latin), not Russian Эра/Эру/Эры/Эре, when referring to zkSync Era
