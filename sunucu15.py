from datetime import datetime
import json
import os
import time
from threading import Thread
from flask import Flask
import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

app = Flask(__name__)

# --- AYARLAR VE SABİTLER ---
MEMORY_FILE_15M = "hafiza_15m.json"
MEMORY_FILE_1H = "hafiza_1h.json"
COOLDOWN_SECONDS = 1800  # Aynı hisse için 30 dakika bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")
NTFY_URL = "https://ntfy.sh/borsa_senet"

# BIST Tüm Hisseler Listesi
STOCKS = [
    "AAVST.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS", "AGROT.IS",
    "AKBNK.IS", "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS", "ALARK.IS",
    "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALMAT.IS", "ANELE.IS", "ANGEN.IS",
    "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARTMS.IS", "ARZUM.IS", "ASELS.IS",
    "ASTOR.IS", "ASUZU.IS", "ATAKP.IS", "ATATP.IS", "ATEKS.IS", "ATLAS.IS", "AVGYO.IS", "AVOD.IS", "AVPGY.IS", "AYCES.IS",
    "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS",
    "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BIENY.IS", "BIGCH.IS", "BIMAS.IS", "BINHO.IS",
    "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", "BMSCH.IS", "BMSTL.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BOSSA.IS",
    "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRLSM.IS", "BRMEN.IS", "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS",
    "BURVA.IS", "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASFY.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEOEM.IS",
    "CGCAM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS",
    "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS", "DESPC.IS",
    "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS", "DOBUR.IS", "DOCO.IS", "DOGUB.IS",
    "DOHOL.IS", "DSTAN.IS", "DUNYA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDIP.IS",
    "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS",
    "ENERY.IS", "ENKAI.IS", "ENJSA.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS",
    "ETILR.IS", "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS", "FADE.IS", "FENER.IS", "FLAP.IS",
    "FMIZP.IS", "FONET.IS", "FORMT.IS", "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENIL.IS",
    "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLCVY.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLTS.IS",
    "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GTRGY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATEK.IS",
    "HATSN.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HURGZ.IS", "ICBCT.IS", "IDEAS.IS",
    "IDGYO.IS", "IENTS.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS",
    "INTEM.IS", "INVEO.IS", "INVES.IS", "IPEKE.IS", "ISATR.IS", "ISBIR.IS", "ISBTR.IS", "ISCEN.IS", "ISCTR.IS", "ISFIN.IS",
    "ISGSY.IS", "ISGYO.IS", "ISKPL.IS", "ISKUR.IS", "ISMEN.IS", "ISSEN.IS", "IZENR.IS", "IZFAS.IS", "IZINV.IS", "JANTS.IS",
    "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KBORU.IS", "KCAER.IS", "KCHOL.IS",
    "KENT.IS", "KERVT.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLRHO.IS", "KLMSN.IS", "KLSER.IS",
    "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS", "KOZAL.IS",
    "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KZBGY.IS", "KZYGZ.IS", "LIDER.IS", "LIDFA.IS",
    "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARTI.IS", "MAVI.IS",
    "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS", "MIATK.IS", "MMCAS.IS",
    "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS", "NETAS.IS",
    "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS", "ORCAY.IS",
    "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "OZRDN.IS", "PAKRD.IS", "PAMEL.IS", "PAPIL.IS", "PARSN.IS",
    "PASEU.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS", "PKART.IS",
    "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS", "QNBFB.IS", "QNBFL.IS",
    "QUAGR.IS", "RALYH.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS", "RYSAS.IS",
    "SAFKR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGFO.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS", "SELEC.IS",
    "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS", "SMRTG.IS", "SNGYO.IS", "SNICA.IS",
    "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TABGD.IS", "TARKM.IS",
    "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEKTU.IS", "TETMT.IS", "TEZOL.IS",
    "TGSAS.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS", "TRMET.IS",
    "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS", "ULUFA.IS",
    "ULKER.IS", "ULUUN.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS",
    "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS", "YGGYO.IS",
    "YIGIT.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS",
]


def piyasa_zaman_kontrolu():
  simdi = datetime.now(TZ_TR)
  if simdi.weekday() >= 5:
    return False
  baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
  bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)
  return baslangic <= simdi <= bitis


def hafiza_yukle(dosya):
  if os.path.exists(dosya):
    try:
      with open(dosya, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafiza_kaydet(dosya, hafiza):
  with open(dosya, "w") as f:
    json.dump(hafiza, f)


def send_ntfy(message, title_prefix):
  try:
    headers = {
        "Title": f"BIST {title_prefix} Sinyal",
        "Priority": "high",
    }
    requests.post(
        NTFY_URL, data=message.encode("utf-8"), headers=headers, timeout=10
    )
  except Exception as e:
    print(f"Bildirim Hatası: {e}")


def calculate_supertrend(df, period=10, multiplier=3):
  hl2 = (df["High"] + df["Low"]) / 2
  tr1 = df["High"] - df["Low"]
  tr2 = (df["High"] - df["Close"].shift(1)).abs()
  tr3 = (df["Low"] - df["Close"].shift(1)).abs()
  tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
  atr = tr.rolling(window=period).mean()

  upper_basic = hl2 + (multiplier * atr)
  lower_basic = hl2 - (multiplier * atr)

  upper_band = upper_basic.copy()
  lower_band = lower_basic.copy()

  direction = pd.Series(1, index=df.index)
  st = pd.Series(index=df.index, dtype="float64")

  for i in range(1, len(df)):
    curr_close = df["Close"].iloc[i]
    if curr_close > upper_band.iloc[i]:
      direction.iloc[i] = 1
    elif curr_close < lower_band.iloc[i]:
      direction.iloc[i] = -1
    else:
      direction.iloc[i] = direction.iloc[i - 1]
      if (
          direction.iloc[i] == 1
          and lower_band.iloc[i] < lower_band.iloc[i - 1]
      ):
        lower_band.iloc[i] = lower_band.iloc[i - 1]
      if (
          direction.iloc[i] == -1
          and upper_band.iloc[i] > upper_band.iloc[i - 1]
      ):
        upper_band.iloc[i] = upper_band.iloc[i - 1]

    st.iloc[i] = (
        lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
    )

  return st


def calculate_hma(series, period=20):
  half_per = period // 2
  sqrt_per = int(np.sqrt(period))

  def wma(s, p):
    weights = np.arange(1, p + 1)
    return s.rolling(p).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )

  wma_half = wma(series, half_per)
  wma_full = wma(series, period)
  raw_hma = 2 * wma_half - wma_full
  hma = wma(raw_hma, sqrt_per)
  return hma


def check_wave_margins(df, lookback=3, threshold_multiplier=0.80):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35 or np.isnan(close[-1]):
      return False

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    if margin_range == 0:
      return False

    upper_margin_threshold = recent_low + (margin_range * threshold_multiplier)

    triggered = False
    for i in range(-lookback, 0):
      if i - 1 < -len(close):
        continue
      prev_p = close[i - 1]
      curr_p = close[i]
      if prev_p <= upper_margin_threshold and curr_p > upper_margin_threshold:
        triggered = True
        break

    return triggered
  except Exception:
    return False


def hesapla_fibonacci(df, window=100):
  recent_df = df.tail(window)
  max_high = recent_df["High"].max()
  min_low = recent_df["Low"].min()
  diff = max_high - min_low

  curr_price = df["Close"].iloc[-1]

  fib_ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
  levels = [min_low + (diff * r) for r in fib_ratios]
  levels.sort()

  destekler = [lvl for lvl in levels if lvl < curr_price]
  direncler = [lvl for lvl in levels if lvl > curr_price]

  ilk_destek = destekler[-1] if destekler else min_low
  ilk_direnc = direncler[0] if direncler else max_high

  return ilk_destek, ilk_direnc


def ortak_tarama_mantigi(df):
  high, low, close, volume = df["High"], df["Low"], df["Close"], df["Volume"]

  st = calculate_supertrend(df)
  st_breakout = close.iloc[-1] > (st.iloc[-1] * 1.002)

  wave_breakout = check_wave_margins(df)

  vol_ma20 = volume.rolling(window=20).mean()
  rvol = volume.iloc[-1] / (vol_ma20.iloc[-1] + 1e-10)
  volume_growth = volume.iloc[-1] > volume.iloc[-2]
  rvol_check = rvol > 0.6

  sma20 = close.rolling(window=20).mean()
  std20 = close.rolling(window=20).std()
  upper_band = sma20 + (std20 * 2)
  bollinger_check = close.iloc[-1] >= upper_band.iloc[-1]

  typical_price = (high + low + close) / 3
  money_flow = typical_price * volume
  positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
  negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
  mfi = 100 - (100 / (1 + (positive_flow / (negative_flow + 1e-10))))
  mfi_curr = mfi.iloc[-1]
  mfi_check = mfi_curr > 29

  up_move = high.diff()
  down_move = -low.diff()
  plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
  tr1 = high - low
  tr2 = (high - close.shift(1)).abs()
  tr3 = (low - close.shift(1)).abs()
  tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
  atr = tr.rolling(14).mean()
  plus_di = (pd.Series(plus_dm, index=df.index).rolling(14).mean() / (atr + 1e-10)) * 100
  plus_di_curr = plus_di.iloc[-1]
  di_check = plus_di_curr > 20

  delta = close.diff()
  gain = delta.where(delta > 0, 0).rolling(14).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
  rs = gain / (loss + 1e-10)
  rsi = 100 - (100 / (1 + rs))
  rsi_curr = rsi.iloc[-1]
  rsi_check = rsi_curr > 50

  sartlar_saglandi = (
      st_breakout
      and wave_breakout
      and volume_growth
      and rvol_check
      and bollinger_check
      and mfi_check
      and di_check
      and rsi_check
  )

  return (
      sartlar_saglandi,
      close.iloc[-1],
      mfi_curr,
      plus_di_curr,
      rsi_curr,
      rvol,
  )


# --- YENİ EKLENEN TARAMA STRATEJİLERİ ---

def check_1h_yakala(df_1h):
  try:
    close = df_1h["Close"]
    high = df_1h["High"]
    low = df_1h["Low"]

    hma20 = calculate_hma(close, 20)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    plus_di = (pd.Series(plus_dm, index=df_1h.index).rolling(14).mean() / (tr.rolling(14).mean() + 1e-10)) * 100

    wave_breakout = check_wave_margins(df_1h, lookback=3, threshold_multiplier=0.80)

    return (close.iloc[-1] > hma20.iloc[-1]) and (rsi.iloc[-1] > 50) and (plus_di.iloc[-1] > 25) and wave_breakout
  except:
    return False


def check_delirdi_1h(df_1h):
  try:
    close = df_1h["Close"]
    volume = df_1h["Volume"]

    hma20 = calculate_hma(close, 20)
    rvol = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
    wave_breakout = check_wave_margins(df_1h, lookback=3, threshold_multiplier=0.80)

    return (close.iloc[-1] > hma20.iloc[-1]) and (rvol >= 2.0) and wave_breakout
  except:
    return False


def check_cekirge(df_15m, df_1h):
  try:
    if df_1h.empty or len(df_1h) < 35:
      return False

    close_1h = df_1h["Close"]
    high_1h = df_1h["High"]
    low_1h = df_1h["Low"]
    volume_1h = df_1h["Volume"]

    hma20_1h = calculate_hma(close_1h, 20)

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high_1h = high_1h.iloc[-total_cycle:].max()
    recent_low_1h = low_1h.iloc[-total_cycle:].min()
    margin_range_1h = recent_high_1h - recent_low_1h

    rvol_1h = volume_1h.iloc[-1] / volume_1h.rolling(20).mean().iloc[-1]
    efficiency_1h = margin_range_1h / (rvol_1h + 1e-5)

    up_move_1h = high_1h.diff()
    down_move_1h = -low_1h.diff()
    plus_dm_1h = np.where((up_move_1h > down_move_1h) & (up_move_1h > 0), up_move_1h, 0.0)
    tr_1h = pd.concat([high_1h - low_1h, (high_1h - close_1h.shift(1)).abs(), (low_1h - close_1h.shift(1)).abs()], axis=1).max(axis=1)
    plus_di_1h = (pd.Series(plus_dm_1h, index=df_1h.index).rolling(14).mean() / (tr_1h.rolling(14).mean() + 1e-10)) * 100

    makro_onay = (efficiency_1h > 0.35) and (plus_di_1h.iloc[-1] > 25.0) and (close_1h.iloc[-1] > hma20_1h.iloc[-1])

    if not makro_onay:
      return False

    close_15m = df_15m["Close"]
    high_15m = df_15m["High"]
    low_15m = df_15m["Low"]
    volume_15m = df_15m["Volume"]

    typical_price_15m = (high_15m + low_15m + close_15m) / 3
    money_flow_15m = typical_price_15m * volume_15m
    pos_flow_15m = money_flow_15m.where(typical_price_15m > typical_price_15m.shift(1), 0).rolling(14).sum()
    neg_flow_15m = money_flow_15m.where(typical_price_15m < typical_price_15m.shift(1), 0).rolling(14).sum()
    mfi_15m = 100 - (100 / (1 + (pos_flow_15m / (neg_flow_15m + 1e-10))))

    mfi_60_sarti = (mfi_15m.iloc[-12:] > 60.0).any()

    lowest_k = low_15m.rolling(14).min()
    highest_k = high_15m.rolling(14).max()
    stoch_k = 100 * (close_15m - lowest_k) / (highest_k - lowest_k + 1e-10)
    stoch_esnek = (stoch_k.iloc[-1] <= 25.0) or (stoch_k.iloc[-1] > stoch_k.iloc[-2])

    hma9_15m = calculate_hma(close_15m, 9)
    tenkan_9 = (high_15m.rolling(9).max() + low_15m.rolling(9).min()) / 2
    kijun_26 = (high_15m.rolling(26).max() + low_15m.rolling(26).min()) / 2
    span_a = (tenkan_9 + kijun_26) / 2
    span_b = (high_15m.rolling(52).max() + low_15m.rolling(52).min()) / 2

    hma_span_a = (hma9_15m.iloc[-2] <= span_a.iloc[-2] and hma9_15m.iloc[-1] > span_a.iloc[-1]) or (hma9_15m.iloc[-1] > span_a.iloc[-1])

    bulut_kalinligi = (span_a - span_b).abs()
    daralan_bulut = bulut_kalinligi.iloc[-1] < bulut_kalinligi.rolling(20).mean().iloc[-1]

    sma20 = close_15m.rolling(20).mean()
    std20 = close_15m.rolling(20).std()
    band_width = ((sma20 + (std20 * 2)) - (sma20 - (std20 * 2))) / (sma20 + 1e-10)
    bb_squeeze = band_width.iloc[-1] < band_width.rolling(20).mean().iloc[-1]
    bb_orta_ustu = close_15m.iloc[-1] >= sma20.iloc[-1]

    mikro_tetik = (bb_squeeze or bb_orta_ustu or daralan_bulut) and hma_span_a and mfi_60_sarti and stoch_esnek

    return makro_onay and mikro_tetik
  except:
    return False


def check_tehlikeli_hibrit(df_15m, df_1h):
  try:
    if df_1h.empty:
      return False

    close_1h = df_1h["Close"]
    high_1h = df_1h["High"]
    low_1h = df_1h["Low"]

    up_move_1h = high_1h.diff()
    down_move_1h = -low_1h.diff()
    plus_dm_1h = np.where((up_move_1h > down_move_1h) & (up_move_1h > 0), up_move_1h, 0.0)
    tr_1h = pd.concat([high_1h - low_1h, (high_1h - close_1h.shift(1)).abs(), (low_1h - close_1h.shift(1)).abs()], axis=1).max(axis=1)
    plus_di_1h = (pd.Series(plus_dm_1h, index=df_1h.index).rolling(14).mean() / (tr_1h.rolling(14).mean() + 1e-10)) * 100

    if plus_di_1h.iloc[-1] <= 25.0:
      return False

    close_15m = df_15m["Close"]
    high_15m = df_15m["High"]
    low_15m = df_15m["Low"]
    volume_15m = df_15m["Volume"]

    hma9_15m = calculate_hma(close_15m, 9)
    tenkan_9 = (high_15m.rolling(9).max() + low_15m.rolling(9).min()) / 2
    kijun_26 = (high_15m.rolling(26).max() + low_15m.rolling(26).min()) / 2
    span_a = (tenkan_9 + kijun_26) / 2
    hma9_esnek = (hma9_15m.iloc[-2] <= span_a.iloc[-2] and hma9_15m.iloc[-1] > span_a.iloc[-1]) or (hma9_15m.iloc[-1] > span_a.iloc[-1])

    up_move_15m = high_15m.diff()
    down_move_15m = -low_15m.diff()
    plus_dm_15m = np.where((up_move_15m > down_move_15m) & (up_move_15m > 0), up_move_15m, 0.0)
    minus_dm_15m = np.where((down_move_15m > up_move_15m) & (down_move_15m > 0), down_move_15m, 0.0)
    tr_15m = pd.concat([high_15m - low_15m, (high_15m - close_15m.shift(1)).abs(), (low_15m - close_15m.shift(1)).abs()], axis=1).max(axis=1)
    plus_di_15m = (pd.Series(plus_dm_15m, index=df_15m.index).rolling(14).mean() / (tr_15m.rolling(14).mean() + 1e-10)) * 100
    minus_di_15m = (pd.Series(minus_dm_15m, index=df_15m.index).rolling(14).mean() / (tr_15m.rolling(14).mean() + 1e-10)) * 100

    di_kesisim_15m = (plus_di_15m.iloc[-2] <= minus_di_15m.iloc[-2]) and (plus_di_15m.iloc[-1] > minus_di_15m.iloc[-1])
    di_15m_kosul = (plus_di_15m.iloc[-1] > 20.0) or di_kesisim_15m

    typical_price_15m = (high_15m + low_15m + close_15m) / 3
    money_flow_15m = typical_price_15m * volume_15m
    pos_flow_15m = money_flow_15m.where(typical_price_15m > typical_price_15m.shift(1), 0).rolling(14).sum()
    neg_flow_15m = money_flow_15m.where(typical_price_15m < typical_price_15m.shift(1), 0).rolling(14).sum()
    mfi_15m = 100 - (100 / (1 + (pos_flow_15m / (neg_flow_15m + 1e-10))))

    hibrit_mfi_onay = (mfi_15m.iloc[-12:] > 70).any() and (mfi_15m.iloc[-4:] > 50).all() and (mfi_15m.iloc[-1] > 50)
    rvol_15m = volume_15m.iloc[-1] / volume_15m.rolling(20).mean().iloc[-1]

    return hma9_esnek and di_15m_kosul and hibrit_mfi_onay and (rvol_15m >= 0.6)
  except:
    return False


def tarama_calistir_15m():
  if not piyasa_zaman_kontrolu():
    return
  hafiza = hafiza_yukle(MEMORY_FILE_15M)
  simdi_epoch = time.time()

  for ticker in STOCKS:
    clean_ticker = ticker.strip()
    try:
      df_15m = yf.download(clean_ticker, period="10d", interval="15m", progress=False)
      df_1h = yf.download(clean_ticker, period="30d", interval="1h", progress=False)

      if df_15m.empty or len(df_15m) < 40:
        continue
      if isinstance(df_15m.columns, pd.MultiIndex):
        df_15m.columns = df_15m.columns.get_level_values(0)
      if not df_1h.empty and isinstance(df_1h.columns, pd.MultiIndex):
        df_1h.columns = df_1h.columns.get_level_values(0)

      sartlar, fiyat, mfi_curr, plus_di_curr, rsi_curr, rvol = ortak_tarama_mantigi(df_15m)

      # Yeni Eklenen Taramalar (15m uç noktası için)
      is_cekirge = check_cekirge(df_15m, df_1h)
      is_tehlikeli_hibrit = check_tehlikeli_hibrit(df_15m, df_1h)

      if sartlar or is_cekirge or is_tehlikeli_hibrit:
        mem_key = f"{clean_ticker}_15m"
        if simdi_epoch - hafiza.get(mem_key, 0) > COOLDOWN_SECONDS:
          temiz_isim = clean_ticker.replace(".IS", "")
          ilk_destek, ilk_direnc = hesapla_fibonacci(df_15m)

          etiketler = []
          if sartlar:
            etiketler.append("🚀 15m Hibrit")
          if is_cekirge:
            etiketler.append("🌿 ÇEKİRGE")
          if is_tehlikeli_hibrit:
            etiketler.append("🟢 TEHLİKELİ HİBRİT")

          etiket_str = " | ".join(etiketler)

          mesaj = (
              f"🚀 *{etiket_str}*\n• Hisse: *{temiz_isim}* | Fiyat: {fiyat:.2f}\n"
              f"• 🟢 İlk Destek (Fib): {ilk_destek:.2f}\n"
              f"• 🔴 İlk Direnç (Fib): {ilk_direnc:.2f}\n"
              f"• MFI: {mfi_curr:.1f} | +DI: {plus_di_curr:.1f} | RSI: {rsi_curr:.1f} | RVOL: {rvol:.2f}"
          )
          send_ntfy(mesaj, etiket_str)
          hafiza[mem_key] = simdi_epoch
          hafiza_kaydet(MEMORY_FILE_15M, hafiza)
    except Exception:
      continue


def tarama_calistir_1h():
  if not piyasa_zaman_kontrolu():
    return
  hafiza = hafiza_yukle(MEMORY_FILE_1H)
  simdi_epoch = time.time()

  for ticker in STOCKS:
    clean_ticker = ticker.strip()
    try:
      df_1h = yf.download(clean_ticker, period="60d", interval="1h", progress=False)
      if df_1h.empty or len(df_1h) < 50:
        continue
      if isinstance(df_1h.columns, pd.MultiIndex):
        df_1h.columns = df_1h.columns.get_level_values(0)

      sartlar, fiyat, mfi_curr, plus_di_curr, rsi_curr, rvol = ortak_tarama_mantigi(df_1h)

      # Yeni Eklenen Taramalar (1h uç noktası için)
      is_1h_yakala = check_1h_yakala(df_1h)
      is_delirdi_1h = check_delirdi_1h(df_1h)

      if sartlar or is_1h_yakala or is_delirdi_1h:
        mem_key = f"{clean_ticker}_1h"
        if simdi_epoch - hafiza.get(mem_key, 0) > COOLDOWN_SECONDS:
          temiz_isim = clean_ticker.replace(".IS", "")
          ilk_destek, ilk_direnc = hesapla_fibonacci(df_1h)

          etiketler = []
          if sartlar:
            etiketler.append("🚀 1h Hibrit")
          if is_1h_yakala:
            etiketler.append("⚫ 1 Saat Yakala")
          if is_delirdi_1h:
            etiketler.append("💥 DELİRDİ 1 Saat")

          etiket_str = " | ".join(etiketler)

          mesaj = (
              f"🚀 *{etiket_str}*\n• Hisse: *{temiz_isim}* | Fiyat: {fiyat:.2f}\n"
              f"• 🟢 İlk Destek (Fib): {ilk_destek:.2f}\n"
              f"• 🔴 İlk Direnç (Fib): {ilk_direnc:.2f}\n"
              f"• MFI: {mfi_curr:.1f} | +DI: {plus_di_curr:.1f} | RSI: {rsi_curr:.1f} | RVOL: {rvol:.2f}"
          )
          send_ntfy(mesaj, etiket_str)
          hafiza[mem_key] = simdi_epoch
          hafiza_kaydet(MEMORY_FILE_1H, hafiza)
    except Exception:
      continue


@app.route("/")
def home():
  return "BIST 15m (48589) ve 1h Hibrit Tarama Sunucusu Aktif!"


@app.route("/tara_15m")
def manual_scan_15m():
  Thread(target=tarama_calistir_15m).start()
  return "15m taraması arka planda tetiklendi!"


@app.route("/tara_1h")
def manual_scan_1h():
  Thread(target=tarama_calistir_1h).start()
  return "1h taraması arka planda tetiklendi!"


@app.route("/tara")
def manual_scan_all():
  Thread(target=tarama_calistir_15m).start()
  Thread(target=tarama_calistir_1h).start()
  return "Hem 15m hem de 1h taramaları arka planda tetiklendi!"


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5001))
  app.run(host="0.0.0.0", port=port)
