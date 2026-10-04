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
COOLDOWN_SECONDS = 3600  # Aynı hisse ve aynı periyot için 1 saat bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

# Ntfy Kanal Ayarı
NTFY_URL = "https://ntfy.sh/borsa_senet"

# Tek Merkezi Hafıza Dosyası
MERKEZI_HAFIZA_DOSYASI = "borsa_hafiza.json"

# BIST Tüm Hisseler
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
    "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARTI.IS",
    "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS", "MIATK.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS",
    "NETAS.IS", "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS",
    "ORCAY.IS", "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "OZRDN.IS", "PAKRD.IS", "PAMEL.IS", "PAPIL.IS",
    "PARSN.IS", "PASEU.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS",
    "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS", "QNBFB.IS",
    "QNBFL.IS", "QUAGR.IS", "RALYH.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS",
    "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGFO.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS",
    "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS", "SMRTG.IS", "SNGYO.IS",
    "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TABGD.IS",
    "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEKTU.IS", "TETMT.IS",
    "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS",
    "TRMET.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS",
    "ULUFA.IS", "ULKER.IS", "ULUUN.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS",
    "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS",
    "YGGYO.IS", "YIGIT.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS",
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


def calculate_strend(df, period=10, multiplier=3):
  hl2 = (df["High"] + df["Low"]) / 2
  tr = pd.concat([
      df["High"] - df["Low"],
      (df["High"] - df["Close"].shift()).abs(),
      (df["Low"] - df["Close"].shift()).abs()
  ], axis=1).max(axis=1)
  atr = tr.rolling(period).mean()
  lowerband = hl2 - (multiplier * atr)
  return lowerband


def calculate_cmf(df, period=20):
  high = df["High"]
  low = df["Low"]
  close = df["Close"]
  volume = df["Volume"]
  
  denom = high - low
  denom = denom.replace(0, 1e-10)
  mf_multiplier = ((close - low) - (high - close)) / denom
  mf_volume = mf_multiplier * volume
  cmf = mf_volume.rolling(period).sum() / (volume.rolling(period).sum() + 1e-10)
  return cmf


def calculate_fisher(df, length=9):
  high = df["High"]
  low = df["Low"]
  close = df["Close"]

  min_low = low.rolling(length).min()
  max_high = high.rolling(length).max()

  price_range = max_high - min_low
  price_range = price_range.replace(0, 1e-10)
  
  price_vals = ((2.0 * (close - min_low) / price_range) - 1.0).values
  val_arr = np.zeros_like(price_vals)
  fish_arr = np.zeros_like(price_vals)
  
  for i in range(len(price_vals)):
    if i == 0:
      val_arr[i] = 0.33 * price_vals[i]
      fish_arr[i] = 0.5 * np.log((1.0 + val_arr[i]) / (1.0 - val_arr[i] + 1e-10))
    else:
      clamped_p = np.clip(price_vals[i], -0.999, 0.999)
      val_arr[i] = 0.33 * clamped_p + 0.67 * val_arr[i-1]
      val_arr[i] = np.clip(val_arr[i], -0.999, 0.999)
      
      fish_val = 0.5 * np.log((1.0 + val_arr[i]) / (1.0 - val_arr[i] + 1e-10))
      fish_arr[i] = 0.5 * fish_val + 0.5 * fish_arr[i-1]

  fish = pd.Series(fish_arr, index=close.index)
  trigger = fish.shift(1).fillna(0)
  return fish, trigger


def check_wave_margins(df, lookback=3):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35 or np.isnan(close[-1]):
      return False, 0.0

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    if margin_range == 0:
      return False, 0.0

    upper_margin_threshold = recent_low + (margin_range * 0.80)
    
    current_price = close[-1]
    konum_yuzde = ((current_price - recent_low) / margin_range) * 100.0
    konum_yuzde = np.clip(konum_yuzde, 0.0, 100.0)

    triggered = False
    for i in range(-lookback, 0):
      prev_p = close[i - 1]
      curr_p = close[i]
      if prev_p <= upper_margin_threshold and curr_p > upper_margin_threshold:
        triggered = True
        break

    return triggered, konum_yuzde
  except Exception:
    return False, 0.0


def hafiza_yukle():
  hafiza = {"kayitlar": {}}
  if os.path.exists(MERKEZI_HAFIZA_DOSYASI):
    try:
      with open(MERKEZI_HAFIZA_DOSYASI, "r") as f:
        data = json.load(f)
        # Eski yapıyla uyumluluk için kontrol
        if isinstance(data, dict):
          if "kayitlar" in data:
            hafiza = data
          else:
            hafiza = {"kayitlar": data}
    except:
      hafiza = {"kayitlar": {}}
  
  # 10 günden (10 * 24 * 3600 saniye) eski kayıtları temizle
  simdi_epoch = time.time()
  on_gun_sn = 10 * 24 * 3600
  temiz_kayitlar = {}
  
  for kural, hisseler in hafiza.get("kayitlar", {}).items():
    temiz_kayitlar[kural] = {}
    if isinstance(hisseler, dict):
      for hisse, detay in hisseler.items():
        # Detay hem eski tip timestamp (float/int) hem yeni tip dict olabilir
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
  bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)

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


def strateji_basari_analizi yap(tum_hafiza):
  """
  Geçmiş taramaların ve stratejilerin başarı oranlarını hesaplar.
  Hangi stratejinin yüzde kaç kazandırdığını ve tutturma oranını bulur.
  """
  kayitlar = tum_hafiza.get("kayitlar", {})
  strateji_istatistikleri = {}

  for kural, hisseler in kayitlar.items():
    basarili_sayisi = 0
    toplam_sinyal = 0
    toplam_yuzde = 0.0

    if isinstance(hisseler, dict):
      for hisse, detay in hisseler.items():
        if isinstance(detay, dict):
          ilk_fiyat = detay.get("ilk_fiyat", 0.0)
          guncel_fiyat = detay.get("son_fiyat", ilk_fiyat)
          if ilk_fiyat > 0:
            toplam_sinyal += 1
            getiri_yuzde = ((guncel_fiyat - ilk_fiyat) / ilk_fiyat) * 100.0
            toplam_yuzde += getiri_yuzde
            if getiri_yuzde > 0:
              basarili_sayisi += 1

    if toplam_sinyal > 0:
      tutturma_orani = (basarili_sayisi / toplam_sinyal) * 100.0
      ortalama_getiri = toplam_yuzde / toplam_sinyal
    else:
      tutturma_orani = 0.0
      ortalama_getiri = 0.0

    strateji_istatistikleri[kural] = {
        "toplam_sinyal": toplam_sinyal,
        "tutturma_orani": tutturma_orani,
        "ortalama_getiri": ortalama_getiri
    }

  return strateji_istatistikleri


def run_scanner():
  if not piyasa_zaman_kontrolu():
    print("Borsa seans saatleri dışındayız veya hafta sonu. Tarama atlanıyor.")
    return

  simdi_epoch = time.time()
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] 40'ar Hisselik Gruplar (Chunks) ile"
      " Profesyonel Merkezi Tarama Başlatılıyor..."
  )

  tum_hafiza = hafiza_yukle()
  toplanan_sinyaller = []

  chunk_size = 40
  stock_chunks = [STOCKS[i:i + chunk_size] for i in range(0, len(STOCKS), chunk_size)]

  def fetch_chunk_data(chunk_idx, chunk):
    print(f"Grup {chunk_idx}/{len(stock_chunks)} indiriliyor ({len(chunk)} hisse)...")
    df_15m_all = download_with_retry(chunk, "15m", "1mo")
    time.sleep(0.2)
    df_1h_all = download_with_retry(chunk, "1h", "2mo")
    return chunk_idx, chunk, df_15m_all, df_1h_all

  chunk_results = []
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(fetch_chunk_data, idx, ch) for idx, ch in enumerate(stock_chunks, 1)]
    for future in concurrent.futures.as_completed(futures):
      try:
        chunk_results.append(future.result())
      except Exception as exc:
        print(f"Grup indirme sırasında hata: {exc}")

  chunk_results.sort(key=lambda x: x[0])

  for chunk_idx, chunk, df_15m_all, df_1h_all in chunk_results:
    for clean_ticker in chunk:
      temiz_isim = clean_ticker.replace(".IS", "")

      tetiklenen_str = []
      guncel_fiyat = 0.0
      toplam_puan = 0.0
      son_d_plus = 0.0
      son_mfi = 0.0

      try:
        df_15m = pd.DataFrame()
        df_1h = pd.DataFrame()

        try:
          if not df_15m_all.empty and isinstance(df_15m_all.columns, pd.MultiIndex) and clean_ticker in df_15m_all.columns.levels[0]:
            df_15m = df_15m_all[clean_ticker].dropna(how="all")
          elif not df_15m_all.empty and len(chunk) == 1:
            df_15m = df_15m_all.copy()
        except:
          pass

        try:
          if not df_1h_all.empty and isinstance(df_1h_all.columns, pd.MultiIndex) and clean_ticker in df_1h_all.columns.levels[0]:
            df_1h = df_1h_all[clean_ticker].dropna(how="all")
          elif not df_1h_all.empty and len(chunk) == 1:
            df_1h = df_1h_all.copy()
        except:
          pass

        if df_15m.empty or df_1h.empty or len(df_15m) < 40 or len(df_1h) < 40:
          continue

        if isinstance(df_15m.columns, pd.MultiIndex):
          df_15m.columns = df_15m.columns.get_level_values(0)
        if isinstance(df_1h.columns, pd.MultiIndex):
          df_1h.columns = df_1h.columns.get_level_values(0)

        # 15m Değişkenler
        close_15 = df_15m["Close"]
        high_15 = df_15m["High"]
        low_15 = df_15m["Low"]
        volume_15 = df_15m["Volume"]
        
        if close_15.isna().iloc[-1] or volume_15.isna().iloc[-1]:
          continue

        close_curr_15 = close_15.iloc[-1]
        guncel_fiyat = close_curr_15

        delta_15 = close_15.diff()
        gain_15 = (delta_15.where(delta_15 > 0, 0)).rolling(14).mean()
        loss_15 = (-delta_15.where(delta_15 < 0, 0)).rolling(14).mean()
        rs_15 = gain_15 / (loss_15 + 1e-10)
        rsi_15 = 100 - (100 / (1 + rs_15))
        rsi_curr_15 = rsi_15.iloc[-1]

        tp_15 = (high_15 + low_15 + close_15) / 3
        mf_15 = tp_15 * volume_15
        pos_flow_15 = mf_15.where(tp_15 > tp_15.shift(1), 0).rolling(14).sum()
        neg_flow_15 = mf_15.where(tp_15 < tp_15.shift(1), 0).rolling(14).sum()
        mfi_15 = 100 - (100 / (1 + (pos_flow_15 / (neg_flow_15 + 1e-10))))
        mfi_curr_15 = mfi_15.iloc[-1]
        son_mfi = mfi_curr_15

        up_move_15 = high_15.diff()
        down_move_15 = -low_15.diff()
        plus_dm_15 = up_move_15.where((up_move_15 > down_move_15) & (up_move_15 > 0), 0)
        minus_dm_15 = down_move_15.where((down_move_15 > up_move_15) & (down_move_15 > 0), 0)
        tr_15 = pd.concat([high_15 - low_15, (high_15 - close_15.shift()).abs(), (low_15 - close_15.shift()).abs()], axis=1).max(axis=1)
        tr_smooth_15 = tr_15.rolling(14).sum()
        plus_di_15 = 100 * (plus_dm_15.rolling(14).sum() / (tr_smooth_15 + 1e-10))
        minus_di_15 = 100 * (minus_dm_15.rolling(14).sum() / (tr_smooth_15 + 1e-10))
        plus_di_curr_15 = plus_di_15.iloc[-1]
        minus_di_curr_15 = minus_di_15.iloc[-1]
        son_d_plus = plus_di_curr_15

        rvol_15 = volume_15 / volume_15.rolling(20).mean()
        rvol_curr_15 = rvol_15.iloc[-1]
        hma20_15 = calculate_hma(close_15, 20)
        sart_wave_15, konum_yuzde_15 = check_wave_margins(df_15m, lookback=5)
        cmf_15 = calculate_cmf(df_15m, 20)
        cmf_curr_15 = cmf_15.iloc[-1]

        # Yardımcı kayıt fonksiyonu (İstatistik ve tekrar sayımı için)
        def kayit_guncelle(kural_adi):
            if kural_adi not in tum_hafiza["kayitlar"]:
                tum_hafiza["kayitlar"][kural_adi] = {}
            
            mevcut_kayit = tum_hafiza["kayitlar"][kural_adi].get(clean_ticker)
            if mevcut_kayit:
                # Daha önce kaydedilmiş, son fiyatı güncelle ve tekrar sayısını artır
                mevcut_kayit["son_fiyat"] = guncel_fiyat
                mevcut_kayit["tekrar_sayisi"] = mevcut_kayit.get("tekrar_sayisi", 1) + 1
                son_zaman = mevcut_kayit.get("zaman", simdi_epoch)
            else:
                # Yeni kayıt
                tum_hafiza["kayitlar"][kural_adi][clean_ticker] = {
                    "zaman": simdi_epoch,
                    "ilk_fiyat": guncel_fiyat,
                    "son_fiyat": guncel_fiyat,
                    "tekrar_sayisi": 1
                }
                son_zaman = 0
            return simdi_epoch - son_zaman > COOLDOWN_SECONDS

        # 1. GİTAN 15 -> DELİRDİ formatı (AKTİF)
        kural_tipi = "gitan_15"
        label = "DELİRDİ"
        if (rvol_curr_15 >= 1.0) and sart_wave_15 and (mfi_curr_15 > 55) and (plus_di_curr_15 > 25):
          if kayit_guncelle(kural_tipi):
            tekrar_ed = tum_hafiza["kayitlar"][kural_tipi][clean_ticker]["tekrar_sayisi"]
            tetiklenen_str.append(f"• 🔴 {label} 15 [Tekrar: {tekrar_ed}x] (RVOL:{rvol_curr_15:.2f}|MFI:{mfi_curr_15:.1f}|+DI:{plus_di_curr_15:.1f})")
            toplam_puan += 35.0

        # 1h Değişkenler
        close_1h = df_1h["Close"]
        high_1h = df_1h["High"]
        low_1h = df_1h["Low"]
        volume_1h = df_1h["Volume"]
        
        if close_1h.isna().iloc[-1] or volume_1h.isna().iloc[-1]:
          continue

        close_curr_1h = close_1h.iloc[-1]
        if guncel_fiyat == 0.0:
          guncel_fiyat = close_curr_1h

        delta_1h = close_1h.diff()
        gain_1h = (delta_1h.where(delta_1h > 0, 0)).rolling(14).mean()
        loss_1h = (-delta_1h.where(delta_1h < 0, 0)).rolling(14).mean()
        rs_1h = gain_1h / (loss_1h + 1e-10)
        rsi_1h = 100 - (100 / (1 + rs_1h))
        rsi_curr_1h = rsi_1h.iloc[-1]

        tp_1h = (high_1h + low_1h + close_1h) / 3
        mf_1h = tp_1h * volume_1h
        pos_flow_1h = mf_1h.where(tp_1h > tp_1h.shift(1), 0).rolling(14).sum()
        neg_flow_1h = mf_1h.where(tp_1h < tp_1h.shift(1), 0).rolling(14).sum()
        mfi_1h = 100 - (100 / (1 + (pos_flow_1h / (neg_flow_1h + 1e-10))))
        mfi_curr_1h = mfi_1h.iloc[-1]

        up_move_1h = high_1h.diff()
        down_move_1h = -low_1h.diff()
        plus_dm_1h = up_move_1h.where((up_move_1h > down_move_1h) & (up_move_1h > 0), 0)
        minus_dm_1h = down_move_1h.where((down_move_1h > up_move_1h) & (down_move_1h > 0), 0)
        tr_1h = pd.concat([high_1h - low_1h, (high_1h - close_1h.shift()).abs(), (low_1h - close_1h.shift()).abs()], axis=1).max(axis=1)
        tr_smooth_1h = tr_1h.rolling(14).sum()
        plus_di_1h = 100 * (plus_dm_1h.rolling(14).sum() / (tr_smooth_1h + 1e-10))
        plus_di_curr_1h = plus_di_1h.iloc[-1]

        rvol_1h = volume_1h / volume_1h.rolling(20).mean()
        rvol_curr_1h = rvol_1h.iloc[-1]

        hma20_1h = calculate_hma(close_1h, 20)
        wave_breakout_1h, _ = check_wave_margins(df_1h, lookback=3)
        fish_1h, trg_1h = calculate_fisher(df_1h, length=9)
        fish_curr_1h, trg_curr_1h = fish_1h.iloc[-1], trg_1h.iloc[-1]

        # 3. DİP HİBRİT
        kural_tipi = "dip_hibrit"
        label = "DİP HİBRİT"
        donem_min_1h = low_1h.rolling(window=50).min()
        donem_max_1h = high_1h.rolling(window=50).max()
        fark_1h = donem_max_1h - donem_min_1h
        konum_yuzde_1h_ser = np.where(fark_1h == 0, 0, ((close_1h - donem_min_1h) / fark_1h) * 100)
        konum_yuzde_1h_curr = konum_yuzde_1h_ser[-1] if isinstance(konum_yuzde_1h_ser, np.ndarray) else konum_yuzde_1h_ser.iloc[-1]
        
        dip_sarti_1h = (0.0 <= konum_yuzde_1h_curr <= 15.0)
        momentum_sarti_15m = (mfi_curr_15 > 60.0) and (plus_di_curr_15 > 30.0) and (cmf_curr_15 > 0.0)

        if dip_sarti_1h and momentum_sarti_15m:
          if kayit_guncelle(kural_tipi):
            tekrar_ed = tum_hafiza["kayitlar"][kural_tipi][clean_ticker]["tekrar_sayisi"]
            tetiklenen_str.append(f"• 🟡 {label} [Tekrar: {tekrar_ed}x] (1H Konum:%{konum_yuzde_1h_curr:.1f}|MFI:{mfi_curr_15:.1f})")
            toplam_puan += 25.0

        # 5. 1 Saat Yakala
        kural_tipi = "1h_dalga_gorsel"
        label = "1 Saat Yakala"
        if (close_curr_1h > hma20_1h.iloc[-1]) and (rsi_curr_1h > 50) and (plus_di_curr_1h > 25) and wave_breakout_1h:
          if kayit_guncelle(kural_tipi):
            tekrar_ed = tum_hafiza["kayitlar"][kural_tipi][clean_ticker]["tekrar_sayisi"]
            tetiklenen_str.append(f"• 🟣 {label} [Tekrar: {tekrar_ed}x] (RSI:{rsi_curr_1h:.1f}|+DI:{plus_di_curr_1h:.1f})")
            toplam_puan += 25.0

        # 6. Deli Gitan 1 Saat
        kural_tipi = "deli_gitan_1h"
        label = "DELİRDİ"
        if (close_curr_1h > hma20_1h.iloc[-1]) and (rvol_curr_1h >= 2.0) and wave_breakout_1h:
          if kayit_guncelle(kural_tipi):
            tekrar_ed = tum_hafiza["kayitlar"][kural_tipi][clean_ticker]["tekrar_sayisi"]
            tetiklenen_str.append(f"• 🟠 {label} 1 Saat [Tekrar: {tekrar_ed}x] (RVOL:{rvol_curr_1h:.2f})")
            toplam_puan += 35.0

        # 8. Erken Hibrit 1 Saat
        kural_tipi = "erken_hibrit_1h"
        label = "ERKEN DELİRDİ"
        trend_1h_ok = (close_curr_1h > hma20_1h.iloc[-1])
        erken_tetik_15m = (rvol_curr_15 >= 2.0) and (75.0 <= konum_yuzde_15 <= 95.0) and sart_wave_15

        if trend_1h_ok and erken_tetik_15m:
          if kayit_guncelle(kural_tipi):
            tekrar_ed = tum_hafiza["kayitlar"][kural_tipi][clean_ticker]["tekrar_sayisi"]
            tetiklenen_str.append(f"• 🔥 {label} [Tekrar: {tekrar_ed}x] (RVOL:{rvol_curr_15:.2f}|Konum:%{konum_yuzde_15:.1f})")
            toplam_puan += 35.0

        if tetiklenen_str:
          if toplam_puan == 0:
            toplam_puan = 30.0

          # Mevcut anlık kazanç yüzdesini hesapla
          ilk_f = tum_hafiza["kayitlar"].get(kural_tipi, {}).get(clean_ticker, {}).get("ilk_fiyat", guncel_fiyat)
          kazanc_yuzde = ((guncel_fiyat - ilk_f) / ilk_f) * 100.0 if ilk_f > 0 else 0.0

          toplanan_sinyaller.append({
              "temiz_isim": temiz_isim,
              "fiyat": guncel_fiyat,
              "kazanc_yuzde": kazanc_yuzde,
              "puan": toplam_puan,
              "stratejiler": tetiklenen_str,
              "d_plus": son_d_plus,
              "mfi": son_mfi
          })
          hafiza_kaydet(tum_hafiza)
          print(f"  > {clean_ticker} inceleniyor... 🎯 Sinyal Yakalandı! (+{toplam_puan} Puan)")
        else:
          print(f"  > {clean_ticker} inceleniyor... [Temiz]")

      except Exception as e:
        print(f"  > Hata oluştu ({clean_ticker}): {e}")
        continue

  # --- STRATEJİ BAŞARI İSTATİSTİKLERİNİ HESAPLA ---
  istatistikler = strateji_basari_analizi_yap(tum_hafiza)
  en_iyi_strateji = "Veri Yok"
  en_yuksek_tutturma = 0.0
  if istatistikler:
    # Tutturma oranına göre sırala
    siralI_strat = sorted(istatistikler.items(), key=lambda x: x[1]["tutturma_orani"], reverse=True)
    en_iyi_strateji, en_iyi_veri = siralI_strat[0]
    en_yuksek_tutturma = en_iyi_veri["tutturma_orani"]

  # --- BİLDİRİM GÖNDERİM MANTIĞI ---
  if toplanan_sinyaller:
    toplanan_sinyaller.sort(key=lambda x: x["puan"], reverse=True)
    zaman_str = datetime.now(TZ_TR).strftime('%d.%m.%Y %H:%M')

    # Profesyonel Özet Başlığı
    analiz_ozeti = (
        f"📊 **PROFESYONEL TARAMA RAPORU & ANALİZ**\n"
        f"🏆 En Başarılı Strateji: `{en_iyi_strateji.upper()}` (Tutturma: %{en_yuksek_tutturma:.1f})\n"
        f"----------------------------------------"
    )

    yuksek_sinyaller = [s for s in toplanan_sinyaller if s["puan"] >= 40.0]
    
    for s in yuksek_sinyaller:
      str_metni = "\n".join(s["stratejiler"])
      hisse_adi_str = s['temiz_isim'].upper()
      p = s['puan']
      kz = s['kazanc_yuzde']
      
      if p >= 60.0:
        baslik_tipi = f"🚀🚀🚀 TOP SİNYAL - {p:.1f} Puan"
      else:
        baslik_tipi = f"🚀🚀 GÜÇLÜ SİNYAL - {p:.1f} Puan"

      kart = (
          f"{analiz_ozeti}\n"
          f"{baslik_tipi}\n"
          f"📌 Hisse: 🟦 {hisse_adi_str} 🟦 | Fiyat: ₺{s['fiyat']:.2f}\n"
          f"📈 Sinyalden Beri Getiri: %{kz:+.2f}\n"
          f"{str_metni}\n"
          f"----------------------------------------"
      )
      send_ntfy(kart, "BIST Zirve Sinyaller")
      time.sleep(1)

    tek_fuzeliler = [s for s in toplanan_sinyaller if s["puan"] < 40.0]
    
    if tek_fuzeliler:
      birlesmis_dict = {}
      for item in tek_fuzeliler:
        hisse = item['temiz_isim']
        temiz_strat_isimleri = []
        for st in item['stratejiler']:
            temiz = st.replace("•", "").strip()
            if temiz not in temiz_strat_isimleri:
                temiz_strat_isimleri.append(temiz)

        if hisse in birlesmis_dict:
            for strat in temiz_strat_isimleri:
                if strat not in birlesmis_dict[hisse]['stratejiler']:
                    birlesmis_dict[hisse]['stratejiler'].append(strat)
            if item['puan'] > birlesmis_dict[hisse]['puan']:
                birlesmis_dict[hisse]['puan'] = item['puan']
                birlesmis_dict[hisse]['d_plus'] = item['d_plus']
                birlesmis_dict[hisse]['mfi'] = item['mfi']
                birlesmis_dict[hisse]['fiyat'] = item['fiyat']
                birlesmis_dict[hisse]['kazanc_yuzde'] = item['kazanc_yuzde']
        else:
            birlesmis_dict[hisse] = {
                'fiyat': item['fiyat'],
                'puan': item['puan'],
                'kazanc_yuzde': item['kazanc_yuzde'],
                'd_plus': item['d_plus'],
                'mfi': item['mfi'],
                'stratejiler': list(temiz_strat_isimleri)
            }

      unique_tek_listesi = [{'hisse': k, **v} for k, v in birlesmis_dict.items()]
      
      batch_size = 3
      total_items = len(unique_tek_listesi)
      total_packages = math.ceil(total_items / batch_size)

      for i in range(0, total_items, batch_size):
        chunk = unique_tek_listesi[i:i + batch_size]
        package_no = (i // batch_size) + 1
        
        icerik_listesi = [
            f"📊 **PROFESYONEL ÖZET** (En İyi Strateji: `{en_iyi_strateji.upper()}` - %{en_yuksek_tutturma:.1f} Başarı)",
            f"🚀 TEK FÜZELİLER RAPORU (Paket {package_no}/{total_packages}) [{zaman_str}]",
            "----------------------------------------"
        ]
        
        for item in chunk:
            hisse = item['hisse'].upper()
            fiyat = f"{item['fiyat']:.2f} TL"
            puan = f"{item['puan']:.1f}"
            kz = f"{item['kazanc_yuzde']:+.2f}%"
            d_plus = f"{item['d_plus']:.2f}"
            mfi = f"{item['mfi']:.1f}"
            strats = ", ".join(item['stratejiler'])
            
            satir = (
                f"🚀 🟦 {hisse} 🟦 : {fiyat} (Getiri: {kz})\n"
                f"   • Taramalar: {strats}\n"
                f"   • Puan: {puan} | D+: {d_plus} | MFI: {mfi}"
            )
            icerik_listesi.append(satir)
            
        icerik_listesi.append("----------------------------------------")
        toplu_tek_mesaj = "\n".join(icerik_listesi)
        send_ntfy(toplu_tek_mesaj, "BIST Tek Füze Sinyalleri")
        time.sleep(1)

  print("\nTüm Hisseler 40'ar gruplar halinde tarandı ve süreç tamamlandı.")


if __name__ == "__main__":
  print("Tarama sistemi başlatıldı...")
  run_scanner()
