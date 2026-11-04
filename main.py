from datetime import datetime
import json
import os
import time
import math
import concurrent.futures
import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

# --- AYARLAR VE SABİTLER ---
COOLDOWN_SECONDS = 3600  # Aynı hisse için 1 saat bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

# Ntfy Kanal Ayarı
NTFY_URL = "https://ntfy.sh/borsa_senet"

# Tek Merkezi Hafıza Dosyası
MERKEZI_HAFIZA_DOSYASI = "borsa_hafiza.json"

# BIST Tüm Hisseler (Verdiğiniz Güncel Liste ile Güncellendi)
STOCKS = [
    "A1CAP.IS", "A1YEN.IS", "AAGYO.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS",
    "AGHOL.IS", "AGROT.IS", "AGYO.IS", "AHGAZ.IS", "AHSGY.IS", "AKBNK.IS", "AKCNS.IS", "AKENR.IS", "AKFGY.IS", "AKFIS.IS",
    "AKFYE.IS", "AKGRT.IS", "AKHAN.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS", "AKSUE.IS", "AKYHO.IS", "ALARK.IS",
    "ALBRK.IS", "ALBTN.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALGYO.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALTIN.IS",
    "ALTNY.IS", "ALVES.IS", "ANELE.IS", "ANGEN.IS", "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS",
    "ARFYE.IS", "ARMGD.IS", "ARSAN.IS", "ARTMS.IS", "ARZUM.IS", "ASELS.IS", "ASGYO.IS", "ASTOR.IS", "ASUZU.IS", "ATAGY.IS",
    "ATAKP.IS", "ATATP.IS", "ATATR.IS", "ATEKS.IS", "ATLAS.IS", "ATSYH.IS", "AVGYO.IS", "AVHOL.IS", "AVOD.IS", "AVPGY.IS",
    "AYCES.IS", "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAHKM.IS", "BAKAB.IS", "BALAT.IS",
    "BALSU.IS", "BANVT.IS", "BARMA.IS", "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BESLR.IS", "BESTE.IS",
    "BETAE.IS", "BEYAZ.IS", "BFREN.IS", "BIENY.IS", "BIGCH.IS", "BIGEN.IS", "BIGTK.IS", "BIMAS.IS", "BINBN.IS", "BINHO.IS",
    "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BKRGY.IS", "BLCYT.IS", "BLUME.IS", "BMSCH.IS", "BMSTL.IS", "BNTAS.IS", "BOBET.IS",
    "BORLS.IS", "BORSK.IS", "BOSSA.IS", "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRLSM.IS", "BRMEN.IS", "BRSAN.IS", "BRYAT.IS",
    "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BULGS.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASA.IS",
    "CATES.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEMZY.IS", "CEOEM.IS", "CGCAM.IS", "CIMSA.IS", "CITAS.IS",
    "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS", "CVKMD.IS", "CWENE.IS",
    "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DCTTR.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS", "DESPC.IS", "DEVA.IS",
    "DGATE.IS", "DGGYO.IS", "DGNMO.IS", "DIRIT.IS", "DITAS.IS", "DMLKT.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS",
    "DOFER.IS", "DOFRB.IS", "DOGUB.IS", "DOHOL.IS", "DOKTA.IS", "DSTKF.IS", "DUNYH.IS", "DURDO.IS", "DURKN.IS", "DYOBY.IS",
    "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECOGR.IS", "ECZYT.IS", "EDATA.IS", "EDIP.IS", "EFOR.IS", "EGEEN.IS", "EGEGY.IS",
    "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKDMR.IS", "EKIM.IS", "EKIZ.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS",
    "EMKEL.IS", "EMNIS.IS", "EMPAE.IS", "ENDAE.IS", "ENERY.IS", "ENJSA.IS", "ENKAI.IS", "ENPRA.IS", "ENSRI.IS", "ENTRA.IS",
    "EPLAS.IS", "ERBOS.IS", "ERCB.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS", "ETILR.IS", "ETYAT.IS",
    "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS", "FADE.IS", "FENER.IS", "FLAP.IS", "FMIZP.IS",
    "FONET.IS", "FORMT.IS", "FORTE.IS", "FRIGO.IS", "FRMPL.IS", "FROTO.IS", "FZLGY.IS", "GARAN.IS", "GARFA.IS", "GATEG.IS",
    "GEDIK.IS", "GEDZA.IS", "GENIL.IS", "GENKM.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS", "GIPTA.IS", "GLBMD.IS", "GLCVY.IS",
    "GLRMK.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLDA.IS", "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS",
    "GRSEL.IS", "GRTHO.IS", "GSDDE.IS", "GSDHO.IS", "GSRAY.IS", "GUBRF.IS", "GUNDG.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS",
    "HATEK.IS", "HATSN.IS", "HDFGS.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HOROZ.IS", "HRKET.IS", "HTTBT.IS",
    "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "ICUGS.IS", "IDGYO.IS", "IEYHO.IS", "IHAAS.IS", "IHEVA.IS", "IHGZT.IS",
    "IHLAS.IS", "IHLGM.IS", "IHYAY.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS", "INTEK.IS", "INTEM.IS", "INTET.IS",
    "INVEO.IS", "INVES.IS", "ISBIR.IS", "ISDMR.IS", "ISFIN.IS", "ISGYO.IS", "ISKPL.IS", "ISMEN.IS", "ISSEN.IS", "ISVEA.IS",
    "IZENR.IS", "IZFAS.IS", "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS", "KARCL.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS",
    "KATMR.IS", "KAYSE.IS", "KBORU.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS", "KERVN.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS",
    "KLGYO.IS", "KLKIM.IS", "KLMSN.IS", "KLNMA.IS", "KLRHO.IS", "KLSER.IS", "KLSYN.IS", "KLYPV.IS", "KMPUR.IS", "KNFRT.IS",
    "KOCMT.IS", "KONKA.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KPEKS.IS", "KRDMA.IS", "KRGYO.IS",
    "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KRVGD.IS", "KSTUR.IS", "KTLEV.IS", "KTSKR.IS", "KUTPO.IS", "KUVVA.IS",
    "KUYAS.IS", "KZBGY.IS", "KZGYO.IS", "LIDER.IS", "LIDFA.IS", "LILAK.IS", "LINK.IS", "LKMNH.IS", "LMKDC.IS", "LOGO.IS",
    "LRSHO.IS", "LUKSK.IS", "LXGYO.IS", "LYDHO.IS", "LYDYE.IS", "MAALT.IS", "MACKO.IS", "MAGEN.IS", "MAKIM.IS", "MAKTK.IS",
    "MANAS.IS", "MARBL.IS", "MARMR.IS", "MARTI.IS", "MASFN.IS", "MAVI.IS", "MCARD.IS", "MEDTR.IS", "MEGAP.IS", "MEGMT.IS",
    "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERIT.IS", "MERKO.IS", "METEN.IS", "METRO.IS", "MEYSU.IS", "MGROS.IS", "MHRGY.IS",
    "MIATK.IS", "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MOGAN.IS", "MOPAS.IS", "MPARK.IS", "MRGYO.IS", "MRSHL.IS",
    "MSGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS", "NETAS.IS", "NETCD.IS", "NETGL.IS", "NIBAS.IS", "NTGAZ.IS",
    "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "ODINE.IS", "OFSYM.IS", "ONCSM.IS", "ONRYT.IS",
    "ORCAY.IS", "ORGE.IS", "ORMA.IS", "ORZAX.IS", "OSMEN.IS", "OSTIM.IS", "OTKAR.IS", "OTTO.IS", "OYAKC.IS", "OYAYO.IS",
    "OYLUM.IS", "OYYAT.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS", "OZRDN.IS", "OZSUB.IS", "OZYSR.IS", "PAGYO.IS", "PAHOL.IS",
    "PAMEL.IS", "PAPIL.IS", "PARSN.IS", "PASEU.IS", "PATEK.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS",
    "PETUN.IS", "PGSUS.IS", "PINSU.IS", "PKART.IS", "PKENT.IS", "PLTUR.IS", "PNLSN.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS",
    "PRDGS.IS", "PRKAB.IS", "PRKME.IS", "PRZMA.IS", "PSDTC.IS", "PSGYO.IS", "QNBFK.IS", "QNBTR.IS", "QUAGR.IS", "QUICK.IS",
    "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RGYAS.IS", "RNPOL.IS", "RODRG.IS", "RTALB.IS", "RUBNS.IS", "RUZYE.IS", "RYGYO.IS",
    "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SAMAT.IS", "SANEL.IS", "SANFM.IS", "SANKO.IS", "SARAE.IS", "SARKY.IS", "SASA.IS",
    "SAYAS.IS", "SDTTR.IS", "SEGMN.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SERNT.IS", "SEYKM.IS",
    "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SKYLP.IS", "SKYMD.IS", "SMART.IS", "SMRTG.IS", "SMRVA.IS", "SNGYO.IS",
    "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOHOE.IS", "SOKE.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SSAAT.IS", "SUMAS.IS",
    "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "SVGYO.IS", "TABGD.IS", "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS",
    "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEHOL.IS", "TEKTU.IS", "TERA.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS",
    "TKNKA.IS", "TKNSA.IS", "TLMAN.IS", "TMPOL.IS", "TMSN.IS", "TNZTP.IS", "TOASO.IS", "TRALT.IS", "TRCAS.IS", "TRENJ.IS",
    "TRGYO.IS", "TRHOL.IS", "TRILC.IS", "TRMET.IS", "TSGYO.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS",
    "TUKAS.IS", "TUPRS.IS", "TUREX.IS", "TURGG.IS", "TURSG.IS", "UCAYM.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS", "ULUFA.IS",
    "ULUSE.IS", "ULUUN.IS", "UNLU.IS", "USAK.IS", "USHOL.IS", "VAKBN.IS", "VAKFA.IS", "VAKFN.IS", "VAKKO.IS", "VANGD.IS",
    "VBTYZ.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS", "VEYAS.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "VRGYO.IS", "VSNMD.IS",
    "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS", "YGGYO.IS", "YIGIT.IS", "YKBNK.IS", "YKSLN.IS",
    "YONGA.IS", "YUNSA.IS", "YYAPI.IS", "YYLGD.IS", "ZEDUR.IS", "ZERGY.IS", "ZGYO.IS", "ZOREN.IS", "ZRGYO.IS"
]


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


def calculate_mfi(high, low, close, volume, period=14):
  try:
    tp = (high + low + close) / 3
    rmf = tp * volume
    delta_tp = tp.diff()
    pos_flow = rmf.where(delta_tp > 0, 0).rolling(period).sum()
    neg_flow = rmf.where(delta_tp < 0, 0).rolling(period).sum()
    mfi = 100 - (100 / (1 + pos_flow / (neg_flow + 1e-10)))
    return mfi
  except:
    return pd.Series(50.0, index=close.index)


def calculate_cmf(high, low, close, volume, period=20):
  try:
    mf_multiplier = ((close - low) - (high - close)) / (high - low + 1e-10)
    mf_volume = mf_multiplier * volume
    cmf = mf_volume.rolling(period).sum() / (volume.rolling(period).sum() + 1e-10)
    return cmf
  except:
    return pd.Series(0.0, index=close.index)


def get_wave_position(df):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values
    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)
    if len(high) < total_cycle:
      total_cycle = len(high)
    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low
    if margin_range == 0:
      return 50.0
    current_close = close[-1]
    pos = ((current_close - recent_low) / margin_range) * 100
    return max(0.0, min(100.0, pos))
  except:
    return 50.0


def check_wave_margins(df, lookback=3, threshold_multiplier=0.80):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35 or np.isnan(close[-1]):
      return False, 50.0

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    current_pos = get_wave_position(df)

    if margin_range == 0:
      return False, current_pos

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

    return triggered, current_pos
  except Exception:
    return False, 50.0


# =========================================================================
# 🦅 KARTAL DALGASI MOTORU (15DK - MFI 70+ İŞTAHLI MODÜL)
# =========================================================================
def scan_kartal_dalgasi(df_15m, df_1h):
    try:
        if df_15m is None or df_1h is None or len(df_15m) < 35 or len(df_1h) < 35:
            return False

        close_1h = df_1h['Close']
        hma20_1h = calculate_hma(close_1h, 20)
        if hma20_1h.empty or close_1h.iloc[-1] <= hma20_1h.iloc[-1]:
            return False

        wave_triggered, _ = check_wave_margins(df_15m, lookback=3, threshold_multiplier=0.80)
        if not wave_triggered:
            return False
            
        high_15m = df_15m['High']
        low_15m = df_15m['Low']
        close_15m = df_15m['Close']
        volume_15m = df_15m['Volume']
        
        wave_sequence = [4, 8, 5, 8, 9]
        total_cycle = sum(wave_sequence)
        if len(close_15m) < total_cycle:
            return False
            
        recent_high = high_15m.iloc[-total_cycle:].max()
        recent_low = low_15m.iloc[-total_cycle:].min()
        margin_range = recent_high - recent_low
        
        rvol = volume_15m / volume_15m.rolling(window=20).mean()
        rvol_curr = rvol.iloc[-1] if not pd.isna(rvol.iloc[-1]) and rvol.iloc[-1] > 0 else 1e-5
        rvol_check = rvol_curr >= 0.6
        
        wave_efficiency = margin_range / rvol_curr
        efficiency_check = wave_efficiency > 0.35

        mfi_ser_15m = calculate_mfi(high_15m, low_15m, close_15m, volume_15m, 14)
        mfi_spike_check = (mfi_ser_15m.iloc[-12:] >= 70.0).any()
        
        return wave_triggered and rvol_check and efficiency_check and mfi_spike_check
    except Exception:
        return False


def hafiza_yukle():
  hafiza = {"kayitlar": {}}
  if os.path.exists(MERKEZI_HAFIZA_DOSYASI):
    try:
      with open(MERKEZI_HAFIZA_DOSYASI, "r") as f:
        data = json.load(f)
        if isinstance(data, dict):
          if "kayitlar" in data:
            hafiza = data
          else:
            hafiza = {"kayitlar": data}
    except:
      hafiza = {"kayitlar": {}}
  
  simdi_epoch = time.time()
  on_gun_sn = 10 * 24 * 3600
  temiz_kayitlar = {}
  
  for kural, hisseler in hafiza.get("kayitlar", {}).items():
    temiz_kayitlar[kural] = {}
    if isinstance(hisseler, dict):
      for hisse, detay in hisseler.items():
        zaman = detay.get("zaman", 0) if isinstance(detay, dict) else detay
        if simdi_epoch - zaman <= on_gun_sn:
          temiz_kayitlar[kural][hisse] = detay if isinstance(detay, dict) else {"zaman": zaman, "ilk_fiyat": 0.0, "tekrar_sayisi": 1}
          
  return {"kayitlar": temiz_kayitlar}


def hafiza_kaydet(hafiza):
  with open(MERKEZI_HAFIZA_DOSYASI, "w") as f:
    json.dump(hafiza, f, indent=4)


def piyasa_zaman_kontrolu():
  if os.environ.get("FORCE_RUN", "false").lower() == "true":
    return True

  simdi = datetime.now(TZ_TR)
  if simdi.weekday() >= 5:
    return False

  baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
  bitis = simdi.replace(hour=18, minute=35, second=0, microsecond=0)

  if baslangic <= simdi <= bitis:
    return True
  return False


def send_ntfy(message, baslik):
  try:
    safe_baslik = baslik.encode("ascii", "ignore").decode("ascii")
    headers = {"Title": safe_baslik, "Priority": "high"}
    res = requests.post(
        NTFY_URL, data=message.encode("utf-8"), headers=headers, timeout=10
    )
    print(f"Ntfy Yanıtı ({safe_baslik}): {res.status_code}")
  except Exception as e:
    print(f"Ntfy Mesaj Hatası: {e}")


def download_with_retry(chunk, interval, period, max_retries=4):
  for attempt in range(1, max_retries + 1):
    try:
      df_all = yf.download(chunk, period=period, interval=interval, group_by='ticker', progress=False, threads=True)
      if df_all is not None and not df_all.empty:
        return df_all
    except Exception as e:
      print(f"  [Uyarı] İndirme hatası ({interval}, Deneme {attempt}/{max_retries}): {e}")
      time.sleep(2 * attempt)
  return pd.DataFrame()


def extract_ticker_df(df_all, clean_ticker, chunk):
  try:
    if df_all is None or df_all.empty:
      return pd.DataFrame()

    if isinstance(df_all.columns, pd.MultiIndex):
      if clean_ticker in df_all.columns.levels[0]:
        sub_df = df_all[clean_ticker].dropna(how="all")
        if not sub_df.empty:
          return sub_df

    if len(chunk) == 1:
      return df_all.copy()

    cols = [col for col in df_all.columns if isinstance(col, tuple) and clean_ticker in col]
    if cols:
      sub_df = df_all.xs(clean_ticker, level=0, axis=1).dropna(how="all")
      if not sub_df.empty:
        return sub_df

  except Exception:
    pass
  return pd.DataFrame()


def run_scanner():
  if not piyasa_zaman_kontrolu():
    print("Borsa seans saatleri dışındayız veya hafta sonu. Tarama atlanıyor.")
    return

  simdi_epoch = time.time()
  is_manual_run = os.environ.get("FORCE_RUN", "false").lower() == "true"
  
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] Erken Avcı Sistemi Başlatıldı... (Manuel Mod: {is_manual_run})"
  )

  tum_hafiza = hafiza_yukle()
  toplanan_sinyaller = []

  chunk_size = 40
  stock_chunks = [STOCKS[i:i + chunk_size] for i in range(0, len(STOCKS), chunk_size)]

  def fetch_chunk_data(chunk_idx, chunk):
    print(f"Grup {chunk_idx}/{len(stock_chunks)} verileri indiriliyor ({len(chunk)} hisse)...")
    df_1h_all = download_with_retry(chunk, "1h", "2mo")
    df_15m_all = download_with_retry(chunk, "15m", "10d")
    return chunk_idx, chunk, df_1h_all, df_15m_all

  chunk_results = []
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(fetch_chunk_data, idx, ch) for idx, ch in enumerate(stock_chunks, 1)]
    for future in concurrent.futures.as_completed(futures):
      try:
        chunk_results.append(future.result())
      except Exception as exc:
        print(f"Grup indirme sırasında hata: {exc}")

  chunk_results.sort(key=lambda x: x[0])

  for chunk_idx, chunk, df_1h_all, df_15m_all in chunk_results:
    for clean_ticker in chunk:
      temiz_isim = clean_ticker.replace(".IS", "")
      tetiklenen_str = []
      guncel_fiyat = 0.0
      toplam_puan = 0.0
      son_rsi = 0.0
      son_rvol = 0.0
      son_mfi = 50.0
      son_plus_di = 0.0
      son_konum = 50.0
      son_cmf = 0.0
      son_roc = 0.0
      
      plus_di_curr_1h = 0.0
      plus_di_prev_1h = 0.0
      hma20_1h_val = 0.0
      close_curr_1h = 0.0
      hma20_1h = pd.Series()

      try:
        def kayit_guncelle(kural_adi):
            if kural_adi not in tum_hafiza["kayitlar"]:
                tum_hafiza["kayitlar"][kural_adi] = {}
            
            mevcut_kayit = tum_hafiza["kayitlar"][kural_adi].get(clean_ticker)
            if mevcut_kayit:
                mevcut_kayit["son_fiyat"] = guncel_fiyat
                mevcut_kayit["tekrar_sayisi"] = mevcut_kayit.get("tekrar_sayisi", 1) + 1
                son_zaman = mevcut_kayit.get("zaman", simdi_epoch)
            else:
                tum_hafiza["kayitlar"][kural_adi][clean_ticker] = {
                    "zaman": simdi_epoch,
                    "ilk_fiyat": guncel_fiyat,
                    "son_fiyat": guncel_fiyat,
                    "tekrar_sayisi": 1
                }
                son_zaman = simdi_epoch
            
            if is_manual_run:
                return True
            return simdi_epoch - son_zaman > COOLDOWN_SECONDS

        # ==========================================
        # 1. 1 SAATLİK VERİ ANALİZİ (Aktif)
        # ==========================================
        df_1h = extract_ticker_df(df_1h_all, clean_ticker, chunk)
        if not df_1h.empty and len(df_1h) >= 40:
          if isinstance(df_1h.columns, pd.MultiIndex):
            df_1h.columns = df_1h.columns.get_level_values(0)

          close_1h = df_1h["Close"]
          high_1h = df_1h["High"]
          low_1h = df_1h["Low"]
          volume_1h = df_1h["Volume"]
          
          if not close_1h.isna().iloc[-1] and not volume_1h.isna().iloc[-1]:
            close_curr_1h = close_1h.iloc[-1]
            guncel_fiyat = close_curr_1h

            delta_1h = close_1h.diff()
            gain_1h = (delta_1h.where(delta_1h > 0, 0)).rolling(14).mean()
            loss_1h = (-delta_1h.where(delta_1h < 0, 0)).rolling(14).mean()
            rs_1h = gain_1h / (loss_1h + 1e-10)
            rsi_curr_1h = (100 - (100 / (1 + rs_1h))).iloc[-1]
            son_rsi = rsi_curr_1h

            mfi_1h = calculate_mfi(high_1h, low_1h, close_1h, volume_1h, 14)
            son_mfi = mfi_1h.iloc[-1]

            up_move_1h = high_1h.diff()
            down_move_1h = -low_1h.diff()
            plus_dm_1h = up_move_1h.where((up_move_1h > down_move_1h) & (up_move_1h > 0), 0)
            tr_1h = pd.concat([high_1h - low_1h, (high_1h - close_1h.shift()).abs(), (low_1h - close_1h.shift()).abs()], axis=1).max(axis=1)
            
            plus_di_series_1h = 100 * (plus_dm_1h.rolling(14).sum() / (tr_1h.rolling(14).sum() + 1e-10))
            plus_di_curr_1h = plus_di_series_1h.iloc[-1]
            plus_di_prev_1h = plus_di_series_1h.iloc[-2] if len(plus_di_series_1h) > 1 else plus_di_curr_1h
            son_plus_di = plus_di_curr_1h

            rvol_curr_1h = (volume_1h / volume_1h.rolling(20).mean()).iloc[-1]
            son_rvol = rvol_curr_1h

            wave_res_1h = check_wave_margins(df_1h, lookback=3, threshold_multiplier=0.80)
            wave_breakout_1h = wave_res_1h[0]
            son_konum = wave_res_1h[1]

            hma20_1h = calculate_hma(close_1h, 20)
            hma20_1h_val = hma20_1h.iloc[-1] if not hma20_1h.empty else 0.0

            if (close_curr_1h > hma20_1h_val) and (rsi_curr_1h > 50) and (plus_di_curr_1h > 25) and wave_breakout_1h:
              if kayit_guncelle("1h_dalga_gorsel"):
                tetiklenen_str.append("1 Saat Yakala")
                toplam_puan += 25.0

            if (close_curr_1h > hma20_1h_val) and (rvol_curr_1h >= 2.0) and wave_breakout_1h:
              if kayit_guncelle("deli_gitan_1h"):
                tetiklenen_str.append("DELİRDİ 1 Saat")
                toplam_puan += 35.0

        # ==========================================
        # 2. 15 DAKİKALIK VERİ ANALİZİ
        # ==========================================
        df_15m = extract_ticker_df(df_15m_all, clean_ticker, chunk)
        if not df_15m.empty and len(df_15m) >= 40:
          if isinstance(df_15m.columns, pd.MultiIndex):
            df_15m.columns = df_15m.columns.get_level_values(0)

          close_15m = df_15m["Close"]
          high_15m = df_15m["High"]
          low_15m = df_15m["Low"]
          volume_15m = df_15m["Volume"]

          if not close_15m.isna().iloc[-1] and not volume_15m.isna().iloc[-1]:
            if guncel_fiyat == 0.0:
              guncel_fiyat = close_15m.iloc[-1]

            mfi_15m = calculate_mfi(high_15m, low_15m, close_15m, volume_15m, 14)
            mfi_curr_15 = mfi_15m.iloc[-1]
            son_mfi = max(son_mfi, mfi_curr_15)

            up_move_15m = high_15m.diff()
            down_move_15m = -low_15m.diff()
            plus_dm_15m = up_move_15m.where((up_move_15m > down_move_15m) & (up_move_15m > 0), 0)
            tr_15m = pd.concat([high_15m - low_15m, (high_15m - close_15m.shift()).abs(), (low_15m - close_15m.shift()).abs()], axis=1).max(axis=1)
            
            plus_di_series_15m = 100 * (plus_dm_15m.rolling(14).sum() / (tr_15m.rolling(14).sum() + 1e-10))
            plus_di_curr_15 = plus_di_series_15m.iloc[-1] if not plus_di_series_15m.empty else 0.0
            son_plus_di = max(son_plus_di, plus_di_curr_15)

            cmf_15m = calculate_cmf(high_15m, low_15m, close_15m, volume_15m, 20)
            cmf_curr_15 = cmf_15m.iloc[-1]
            son_cmf = max(son_cmf, cmf_curr_15)

            son_konum = max(son_konum, get_wave_position(df_15m))

            hma20_15m = calculate_hma(close_15m, 20)
            hma20_15m_val = hma20_15m.iloc[-1] if not hma20_15m.empty else close_15m.iloc[-1]

            rvol_15m = volume_15m / volume_15m.rolling(20).mean()
            rvol_curr_15 = rvol_15m.iloc[-1] if not pd.isna(rvol_15m.iloc[-1]) else 1.0

            wave_triggered_15m, _ = check_wave_margins(df_15m, lookback=3, threshold_multiplier=0.80)
            mfi_12_spike = (mfi_15m.iloc[-12:] >= 70.0).any()
            mfi_current_above_50 = mfi_curr_15 >= 50.0
            
            hma_check = (hma20_1h_val <= close_curr_1h) or ((hma20_1h.iloc[-2] < close_1h.iloc[-2]) and (hma20_1h.iloc[-1] >= close_1h.iloc[-1])) if not hma20_1h.empty else False
            di_check = (plus_di_curr_1h >= 25.0) or ((plus_di_prev_1h < 25.0) and (plus_di_curr_1h >= 25.0))

            if hma_check and di_check and wave_triggered_15m and mfi_12_spike and mfi_current_above_50:
              if kayit_guncelle("yakala_15dk"):
                tetiklenen_str.append("YAKALA 15 DK")
                toplam_puan += 30.0

            wave_breakout_15m, _ = check_wave_margins(df_15m, lookback=3, threshold_multiplier=0.80)
            deli_hma_check = close_15m.iloc[-1] > hma20_15m_val
            deli_rvol_check = rvol_curr_15 >= 1.2
            deli_di_check = (plus_di_series_15m.iloc[-12:] >= 25.0).any()
            deli_mfi_check = mfi_curr_15 >= 60.0

            if deli_hma_check and deli_rvol_check and wave_breakout_15m and deli_di_check and deli_mfi_check:
              if kayit_guncelle("delirdi_15dk"):
                tetiklenen_str.append("DELİRDİ 15 DK")
                toplam_puan += 35.0

            tenkan_9 = (high_15m.rolling(9).max() + low_15m.rolling(9).min()) / 2
            kijun_26 = (high_15m.rolling(26).max() + low_15m.rolling(26).min()) / 2

            ichimoku_kesisim = (tenkan_9.iloc[-2] <= kijun_26.iloc[-2]) and (tenkan_9.iloc[-1] > kijun_26.iloc[-1])
            ichimoku_ustunde = tenkan_9.iloc[-1] >= kijun_26.iloc[-1]
            ichimoku_trigger = ichimoku_kesisim or ichimoku_ustunde

            konum_yuzde_1h_curr = check_wave_margins(df_1h, lookback=1)[1] if not df_15m.empty else get_wave_position(df_15m)
            if (0.0 <= konum_yuzde_1h_curr <= 15.0) and (mfi_curr_15 > 50.0) and (plus_di_curr_15 > 20.0) and (cmf_curr_15 > 0.0) and ichimoku_trigger:
              if kayit_guncelle("dip_hibrit"):
                tetiklenen_str.append("TEHLİKELİ HİBRİT")
                toplam_puan += 30.0

            if not df_1h.empty:
                if scan_kartal_dalgasi(df_15m, df_1h):
                    if kayit_guncelle("kartal_dalgasi"):
                        tetiklenen_str.append("KARTAL DALGASI")
                        toplam_puan += 35.0

        # ==========================================
        # 3. YENİ SÜPER 15 CROSS MODÜLÜ
        # ==========================================
        if not df_15m.empty and len(df_15m) >= 40:
          close_s15 = df_15m["Close"]
          high_s15 = df_15m["High"]
          low_s15 = df_15m["Low"]
          volume_s15 = df_15m["Volume"]

          if not close_s15.isna().iloc[-1] and not volume_s15.isna().iloc[-1]:
            if guncel_fiyat == 0.0:
              guncel_fiyat = close_s15.iloc[-1]

            nine_high = high_15m.rolling(window=9).max()
            nine_low = low_15m.rolling(window=9).min()
            tenkan_s15 = (nine_high + nine_low) / 2

            twenty_six_high = high_15m.rolling(window=26).max()
            twenty_six_low = low_15m.rolling(window=26).min()
            kijun_s15 = (twenty_six_high + twenty_six_low) / 2

            span_a = (tenkan_s15 + kijun_s15) / 2
            
            fifty_two_high = high_15m.rolling(window=52).max()
            fifty_two_low = low_15m.rolling(window=52).min()
            span_b = (fifty_two_high + fifty_two_low) / 2

            cloud_width = (span_a - span_b).abs()
            is_cloud_narrowing = cloud_width.iloc[-1] < cloud_width.iloc[-2]

            hma9_s15 = calculate_hma(close_s15, 9)
            hma9_val = hma9_s15.iloc[-1] if not hma9_s15.empty else close_s15.iloc[-1]
            hma9_prev = hma9_s15.iloc[-2] if len(hma9_s15) > 1 else hma9_val

            span_a_val = span_a.iloc[-1] if not span_a.empty else close_s15.iloc[-1]
            span_a_prev = span_a.iloc[-2] if len(span_a) > 1 else span_a_val

            hma_span_cross = (hma9_prev <= span_a_prev and hma9_val > span_a_val) or (hma9_val >= span_a_val)

            up_move_s15 = high_s15.diff()
            down_move_s15 = -low_s15.diff()
            plus_dm_s15 = up_move_s15.where((up_move_s15 > down_move_s15) & (up_move_s15 > 0), 0)
            tr_s15 = pd.concat([high_s15 - low_s15, (high_s15 - close_s15.shift()).abs(), (low_s15 - close_s15.shift()).abs()], axis=1).max(axis=1)
            plus_di_s15 = 100 * (plus_dm_s15.rolling(14).sum() / (tr_s15.rolling(14).sum() + 1e-10))
            plus_di_curr_s15 = plus_di_s15.iloc[-1] if not plus_di_s15.empty else 0.0
            di_check_s15 = plus_di_curr_s15 >= 20.0

            roc_s15 = close_s15.pct_change(periods=2) * 100
            roc_curr_s15 = roc_s15.iloc[-1]
            son_roc = max(son_roc, roc_curr_s15)
            is_sudden_burst = roc_curr_s15 >= 1.5

            mfi_s15 = calculate_mfi(high_s15, low_s15, close_s15, volume_s15, 14)
            mfi_curr_s15 = mfi_s15.iloc[-1]
            son_mfi = max(son_mfi, mfi_curr_s15)

            if hma_span_cross and is_cloud_narrowing and di_check_s15 and is_sudden_burst and (mfi_curr_s15 > 50.0):
              if kayit_guncelle("super_15_bb_cross"):
                tetiklenen_str.append("SÜPER 15 CROSS (HMA9)")
                toplam_puan += 40.0

        if tetiklenen_str:
          if toplam_puan == 0:
            toplam_puan = 25.0

          try:
              live_tk = yf.Ticker(clean_ticker)
              live_price = live_tk.fast_info['lastPrice']
              if live_price is not None and not math.isnan(float(live_price)) and float(live_price) > 0:
                  guncel_fiyat = float(live_price)
          except Exception:
              pass

          toplanan_sinyaller.append({
              "temiz_isim": temiz_isim,
              "fiyat": guncel_fiyat,
              "puan": toplam_puan,
              "stratejiler": tetiklenen_str,
              "rsi": son_rsi,
              "rvol": son_rvol,
              "mfi": son_mfi,
              "plus_di": son_plus_di,
              "konum": son_konum,
              "cmf": son_cmf,
              "roc": son_roc
          })
          hafiza_kaydet(tum_hafiza)
          print(f"  > {clean_ticker} inceleniyor... 🎯 Sinyal Yakalandı! (Fiyat: ₺{guncel_fiyat:.2f})")
        else:
          print(f"  > {clean_ticker} inceleniyor... [Temiz]")

      except Exception as e:
        print(f"  > Hata oluştu ({clean_ticker}): {e}")
        continue

  if toplanan_sinyaller:
    toplanan_sinyaller.sort(key=lambda x: (len(x['stratejiler']), x['puan']), reverse=False)

    grup_boyutu = 5
    for i in range(0, len(toplanan_sinyaller), grup_boyutu):
      alt_grup = toplanan_sinyaller[i:i + grup_boyutu]
      mesaj_satirlari = ["----------------------------------------"]

      for item in alt_grup:
        strats_upper = [s.upper() for s in item['stratejiler']]
        has_both_1h = ("1 SAAT YAKALA" in strats_upper) and ("DELİRDİ 1 SAAT" in strats_upper)

        if has_both_1h:
          prefix = "👑🚨 DİKKAT: 1S ÇİFTE ALARM 👑🚨"
        elif len(item['stratejiler']) >= 3:
          prefix = "🚀🚀🚀 Hisse:"
        else:
          prefix = "📌 Hisse:"
        
        mesaj_satirlari.append(f"{prefix} 🟦 {item['temiz_isim']} 🟦 | Fiyat: ₺{item['fiyat']:.2f}")
        
        for strat in item['stratejiler']:
          strat_upper = strat.upper()
          if "DELİRDİ 15 DK" in strat_upper:
            mesaj_satirlari.append(f"• 🚀🔥 {strat} (RVOL:{item['rvol']:.2f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f})")
          elif "YAKALA 15 DK" in strat_upper:
            mesaj_satirlari.append(f"• 🎯⚡ {strat} (MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | Konum:%{item['konum']:.1f})")
          elif "TEHLİKELİ HİBRİT" in strat_upper:
            mesaj_satirlari.append(f"• 🟢🟢🟢 {strat} (MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | CMF:{item['cmf']:.2f} | Konum:%{item['konum']:.1f})")
          elif "KARTAL DALGASI" in strat_upper:
            mesaj_satirlari.append(f"• 🦅📊 {strat} (MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | Konum:%{item['konum']:.1f})")
          elif "DELİRDİ" in strat_upper and "1 SAAT" in strat_upper:
            mesaj_satirlari.append(f"• 💥💥💥 {strat} (RVOL:{item['rvol']:.2f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | Konum:%{item['konum']:.1f})")
          elif "SÜPER 15 CROSS" in strat_upper:
            mesaj_satirlari.append(f"• 🎯🎯 {strat} (ROC:%{item['roc']:.1f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f})")
          elif "1 SAAT YAKALA" in strat_upper:
            mesaj_satirlari.append(f"• ⚫⚫⚫ {strat} (RSI:{item['rsi']:.1f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f})")
          else:
            mesaj_satirlari.append(f"• 🟣 {strat} (RSI:{item['rsi']:.1f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f})")
            
        mesaj_satirlari.append("----------------------------------------")

      final_mesaj = "\n".join(mesaj_satirlari)
      send_ntfy(final_mesaj, "borsa_senet")
      time.sleep(0.4)

  print("\nTüm Hisseler tarandı ve süreç tamamlandı.")


if __name__ == "__main__":
  print("Tarama Sistemi başlatıldı...")
  run_scanner()
