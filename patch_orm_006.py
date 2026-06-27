import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\backend\orm_models.py'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1); ok.append(label)
    else:
        fail.append(label)

# A) AftaleStatusEnum — afstem med prototypen
sub(
'''class AftaleStatusEnum(str, enum.Enum):
    planlagt      = "planlagt"
    gennemfoert   = "gennemfoert"
    aflyst        = "aflyst"
    udsat         = "udsat"''',
'''class AftaleStatusEnum(str, enum.Enum):
    planlagt      = "planlagt"
    gennemfoert   = "gennemfoert"
    aflyst        = "aflyst"
    udsat         = "udsat"
    kladde        = "kladde"
    pending       = "pending"
    confirmed     = "confirmed"
    afslaaet      = "afslaaet"
    brudt         = "brudt"''',
"A: AftaleStatusEnum")

# B) Nye enums efter NotifTypeEnum
sub(
'''    paamindelse     = "paamindelse"
    system          = "system"''',
'''    paamindelse     = "paamindelse"
    system          = "system"


class UclaSlagsEnum(str, enum.Enum):
    baseline    = "baseline"
    opfoelgning = "opfoelgning"


class OpkaldTypeEnum(str, enum.Enum):
    samtale_menneske  = "samtale_menneske"
    samtale_brobygger = "samtale_brobygger"
    ringeopgave       = "ringeopgave"''',
"B: nye enums")

# C) BrobyggerORM — afdeling + telefon_norm
sub(
'''    hq              = Column(String, nullable=True)
    kon             = Column(String, nullable=True)
    bio             = Column(Text, nullable=True)''',
'''    hq              = Column(String, nullable=True)
    afdeling        = Column(String, nullable=True)
    telefon_norm    = Column(String, nullable=True, index=True)
    kon             = Column(String, nullable=True)
    bio             = Column(Text, nullable=True)''',
"C: BrobyggerORM kolonner")

# D) MenneskORM — nye kolonner
sub(
'''    hq                  = Column(String, nullable=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, default=func.now())''',
'''    hq                  = Column(String, nullable=True)
    afdeling            = Column(String, nullable=True)
    kilde               = Column(String, nullable=True)
    meetpoint           = Column(String, nullable=True)
    sroi_maalgruppe     = Column(String, nullable=True)
    helbreds_kategorier = Column(ARRAY(String), nullable=True)
    praeferencer        = Column(JSON, nullable=True)
    afslut_trivsel      = Column(Integer, nullable=True)
    afslut_aarsag       = Column(String, nullable=True)
    ucla_fravalgt       = Column(Boolean, nullable=False, default=False)
    telefon_norm        = Column(String, nullable=True, index=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, default=func.now())''',
"D: MenneskORM kolonner")

# E) MenneskORM — nye relationer
sub(
'''    samtykker   = relationship("SamtykkeORM",  back_populates="menneske", cascade="all, delete-orphan")''',
'''    samtykker   = relationship("SamtykkeORM",  back_populates="menneske", cascade="all, delete-orphan")
    henvendelser    = relationship("HenvendelseORM",  back_populates="menneske", cascade="all, delete-orphan")
    ucla_maalinger  = relationship("UclaMaalingORM",  back_populates="menneske", cascade="all, delete-orphan")
    kontaktpersoner = relationship("KontaktpersonORM", back_populates="menneske", cascade="all, delete-orphan")''',
"E: MenneskORM relationer")

# F) AftaleORM — nye kolonner
sub(
'''    notes           = Column(Text, nullable=False, default="")
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())''',
'''    notes           = Column(Text, nullable=False, default="")
    # Klassificering (fra stamdata)
    aftaletype          = Column(String, nullable=True)
    brobygningstype     = Column(String, nullable=True)   # Social|Forening|Sundhed
    henvender           = Column(String, nullable=True)
    modtager            = Column(String, nullable=True)
    finansiering        = Column(String, nullable=True)
    samarbejdspartner   = Column(String, nullable=True)
    afdeling            = Column(String, nullable=True)
    aflyst_af           = Column(String, nullable=True)
    aflysnings_aarsag   = Column(String, nullable=True)
    transportplan       = Column(String, nullable=True)
    aktivitets_tid      = Column(String, nullable=True)
    fremmoede_type      = Column(String, nullable=True)
    gentagelse          = Column(String, nullable=True)
    aftale_form         = Column(String, nullable=True)
    brobygger_note      = Column(Text, nullable=True)     # briefing til brobygger
    raadgiver_opfoelgning = Column(Text, nullable=True)
    # brobyggerLog (udfald af afholdt aftale)
    udfald          = Column(String, nullable=True)        # gennemfoert|afbud|ikke-modt
    varighed_min    = Column(Integer, nullable=True)
    log_note        = Column(Text, nullable=True)
    logged_at       = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())''',
"F: AftaleORM kolonner")

# G) Nye modeller i slutningen
NEW = '''


# ═══════════════════════════════════════════════════════════════════════════════
# STAMDATA (admin-redigerbart reference-data — erstatter SoS_REFS)
# ═══════════════════════════════════════════════════════════════════════════════

class StamdataORM(Base):
    __tablename__ = "stamdata"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kategori    = Column(Text, nullable=False, index=True)
    navn        = Column(Text, nullable=False)
    hovedsaede  = Column(Text, nullable=True)   # NULL/'Alle hovedsæder' = landsdækkende
    farve       = Column(Text, nullable=True)
    sort_order  = Column(Integer, nullable=False, default=0)
    aktiv       = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ═══════════════════════════════════════════════════════════════════════════════
# HENVENDELSER (flere pr. menneske; tidligste = førstegangshenvender)
# ═══════════════════════════════════════════════════════════════════════════════

class HenvendelseORM(Base):
    __tablename__ = "henvendelser"

    id             = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menneske_id    = Column(PG_UUID(as_uuid=True), ForeignKey("mennesker.id", ondelete="CASCADE"), nullable=False)
    type           = Column(Text, nullable=False)
    navn           = Column(Text, nullable=True)
    dato           = Column(Date, nullable=False)
    note           = Column(Text, nullable=True)
    oprettet_af_id = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=True)
    created_at     = Column(DateTime(timezone=True), nullable=False, default=func.now())

    menneske = relationship("MenneskORM", back_populates="henvendelser")


# ═══════════════════════════════════════════════════════════════════════════════
# UCLA-3 MÅLINGER (ensomhed: baseline + opfølgninger)
# ═══════════════════════════════════════════════════════════════════════════════

class UclaMaalingORM(Base):
    __tablename__ = "ucla_maalinger"

    id             = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menneske_id    = Column(PG_UUID(as_uuid=True), ForeignKey("mennesker.id", ondelete="CASCADE"), nullable=False)
    slags          = Column(PgEnum(UclaSlagsEnum, name="ucla_slags"), nullable=False)
    q1             = Column(Integer, nullable=True)
    q2             = Column(Integer, nullable=True)
    q3             = Column(Integer, nullable=True)
    sum            = Column(Integer, nullable=False)   # 3–9
    dato           = Column(Date, nullable=False)
    label          = Column(Text, nullable=True)
    oprettet_af_id = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=True)
    created_at     = Column(DateTime(timezone=True), nullable=False, default=func.now())

    menneske = relationship("MenneskORM", back_populates="ucla_maalinger")


# ═══════════════════════════════════════════════════════════════════════════════
# UDLÆG-KONTI (bankoplysninger — kontonr KRYPTERET)
# ═══════════════════════════════════════════════════════════════════════════════

class UdlaegKontoORM(Base):
    __tablename__ = "udlaeg_konti"

    id           = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brobygger_id = Column(PG_UUID(as_uuid=True), ForeignKey("brobyggere.id", ondelete="CASCADE"), nullable=False, unique=True)
    navn         = Column(Text, nullable=False)
    email        = Column(Text, nullable=True)
    reg_nr       = Column(Text, nullable=False)
    konto_nr_enc = Column(BYTEA, nullable=False)   # pgp_sym_encrypt — som helbredsnoter
    aar          = Column(Integer, nullable=False)
    kreditor_nr  = Column(Text, nullable=True)
    indsendt_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ═══════════════════════════════════════════════════════════════════════════════
# OPKALDS-LOG (typed; koblet til menneske ELLER brobygger)
# ═══════════════════════════════════════════════════════════════════════════════

class OpkaldLogORM(Base):
    __tablename__ = "opkald_log"

    id             = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type           = Column(PgEnum(OpkaldTypeEnum, name="opkald_type"), nullable=False)
    under_type     = Column(Text, nullable=True)
    menneske_id    = Column(PG_UUID(as_uuid=True), ForeignKey("mennesker.id", ondelete="SET NULL"), nullable=True)
    brobygger_id   = Column(PG_UUID(as_uuid=True), ForeignKey("brobyggere.id", ondelete="SET NULL"), nullable=True)
    tlf            = Column(Text, nullable=True)
    note           = Column(Text, nullable=False)
    dato           = Column(Date, nullable=False)
    tid            = Column(Text, nullable=True)
    oprettet_af_id = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=True)
    created_at     = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ═══════════════════════════════════════════════════════════════════════════════
# BESKED-SKABELONER (pr. rådgiver; flettefelter i tekst)
# ═══════════════════════════════════════════════════════════════════════════════

class BeskedSkabelonORM(Base):
    __tablename__ = "besked_skabeloner"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ejer_id     = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id", ondelete="CASCADE"), nullable=False)
    navn        = Column(Text, nullable=False)
    indsats     = Column(String, nullable=False, default="alle")
    tekst       = Column(Text, nullable=False)
    er_standard = Column(Boolean, nullable=False, default=False)
    created_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ═══════════════════════════════════════════════════════════════════════════════
# KONTAKTPERSONER (pårørende/instans pr. menneske)
# ═══════════════════════════════════════════════════════════════════════════════

class KontaktpersonORM(Base):
    __tablename__ = "kontaktpersoner"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menneske_id = Column(PG_UUID(as_uuid=True), ForeignKey("mennesker.id", ondelete="CASCADE"), nullable=False)
    rolle       = Column(Text, nullable=True)
    navn        = Column(Text, nullable=True)
    tlf         = Column(Text, nullable=True)

    menneske = relationship("MenneskORM", back_populates="kontaktpersoner")
'''
c = c.rstrip() + "\n" + NEW

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)
