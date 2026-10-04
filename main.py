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
COOLDOWN_SECONDS = 3600  # Normal taramada aynı hisse için 1 saat bekleme süresi
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


def strateji_basari_analizi_yap(tum_hafiza):
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


def performans_raporu_gonder(rapor_turu="Gün Sonu"):
  print(f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] BIST {rapor_turu} Raporu hazırlanıyor...")
  tum_hafiza = hafiza_yukle()
  kayitlar = tum_hafiza.get("kayitlar", {})

  if not kayitlar:
    print("Hafızada raporlanacak sinyal bulunamadı.")
    return

  tum_hisseler = set()
  for kural, hisseler in kayitlar.items():
    if isinstance(hisseler, dict):
      for hisse in hisseler.keys():
        tum_hisseler.add(hisse + ".IS")

  if tum_hisseler:
    try:
      df_guncel = download_with_retry(list(tum_hisseler), "15m", "5d")
      for kural, hisseler in kayitlar.items():
        if isinstance(hisseler, dict):
          for hisse, detay in hisseler.items():
            full_t = hisse + ".IS"
            try:
              sub_f = extract_ticker_df(df_guncel, full_t, list(tum_hisseler))
              if not sub_f.empty and "Close" in sub_f.columns:
                s_close = sub_f["Close"].dropna()
                if not s_close.empty:
                  detay["son_fiyat"] = float(s_close.iloc[-1])
            except:
              pass
      hafiza_kaydet(tum_hafiza)
    except Exception as e:
      print(f"Performans raporu fiyat güncelleme hatası: {e}")

  strat_istatistikleri = strateji_basari_analizi_yap(tum_hafiza)

  simdi_tr = datetime.now(TZ_TR)
  bugun_tarih = simdi_tr.date()

  hisse_getirileri = {}
  for kural, hisseler in kayitlar.items():
    if isinstance(hisseler, dict):
      for hisse, detay in hisseler.items():
        if isinstance(detay, dict):
          ilk = detay.get("ilk_fiyat", 0.0)
          son = detay.get("son_fiyat", ilk)
          zaman_epoch = detay.get("zaman", time.time())
          
          if ilk > 0:
            getiri = ((son - ilk) / ilk) * 100.0
            sinyal_tarihi = datetime.fromtimestamp(zaman_epoch, TZ_TR).date()
            gun_farki = (bugun_tarih - sinyal_tarihi).days
            
            if gun_farki == 0:
              sure_str = "Bugün"
            elif gun_farki == 1:
              sure_str = "Dün"
            else:
              sure_str = f"{gun_farki}G"

            hisse_getirileri[hisse] = {
                "getiri": getiri, 
                "kural": kural, 
                "sure": sure_str
            }

  sirali_hisseler = sorted(hisse_getirileri.items(), key=lambda x: x[1]["getiri"], reverse=True)

  if not sirali_hisseler:
    print("Rapor oluşturuldu ancak listelenecek aktif sinyal/getiri verisi bulunamadı.")
    return

  mesaj_satirlari = [f"BIST {rapor_turu} Raporu", "En İyi Sinyaller:"]

  for hisse, veri in sirali_hisseler[:6]:
    g = veri["getiri"]
    g_str = f"+%{g:.1f}" if g >= 0 else f"%{g:.1f}"
    strat_adi = veri["kural"][:6].upper()
    mesaj_satirlari.append(f"• {hisse.upper()}: {g_str} ({strat_adi})")

  final_mesaj = "\n".join(mesaj_satirlari)
  send_ntfy(final_mesaj, f"BIST {rapor_turu} Raporu")
  print(f"BIST {rapor_turu} Raporu başarıyla gönderildi.")


def run_scanner():
  if not piyasa_zaman_kontrolu():
    print("Borsa seans saatleri dışındayız veya hafta sonu. Tarama atlanıyor.")
    return

  simdi_epoch = time.time()
  is_manual_run = os.environ.get("FORCE_RUN", "false").lower() == "true"
  
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] 40'ar Hisselik Gruplar (Chunks) ile"
      f" Profesyonel Merkezi Tarama Başlatıldı... (Manuel Mod: {is_manual_run})"
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
        df_15m = extract_ticker_df(df_15m_all, clean_ticker, chunk)
        df_1h = extract_ticker_df(df_1h_all, clean_ticker, chunk)

        if df_15m.empty or df_1h.empty or len(df_15m) < 40 or len(df_1h) < 40:
          continue

        if isinstance(df_15m.columns, pd.MultiIndex):
          df_15m.columns = df_15m.columns.get_level_values(0)
        if isinstance(df_1h.columns, pd.MultiIndex):
          df_1h.columns = df_1h.columns.get_level_values(0)

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
                son_zaman = 0
            
            if is_manual_run:
                return True

            return simdi_epoch - son_zaman > COOLDOWN_SECONDS

        kural_tipi = "gitan_15"
        label = "D15"
        if (rvol_curr_15 >= 1.0) and sart_wave_15 and (mfi_curr_15 > 55) and (plus_di_curr_15 > 25):
          if kayit_guncelle(kural_tipi):
            tetiklenen_str.append(label)
            toplam_puan += 35.0

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

        kural_tipi = "dip_hibrit"
        label = "DİP"
        donem_min_1h = low_1h.rolling(window=50).min()
        donem_max_1h = high_1h.rolling(window=50).max()
        fark_1h = donem_max_1h - donem_min_1h
        konum_yuzde_1h_ser = np.where(fark_1h == 0, 0, ((close_1h - donem_min_1h) / fark_1h) * 100)
        konum_yuzde_1h_curr = konum_yuzde_1h_ser[-1] if isinstance(konum_yuzde_1h_ser, np.ndarray) else konum_yuzde_1h_ser.iloc[-1]
        
        dip_sarti_1h = (0.0 <= konum_yuzde_1h_curr <= 15.0)
        momentum_sarti_15m = (mfi_curr_15 > 60.0) and (plus_di_curr_15 > 30.0) and (cmf_curr_15 > 0.0)

        if dip_sarti_1h and momentum_sarti_15m:
          if kayit_guncelle(kural_tipi):
            tetiklenen_str.append(label)
            toplam_puan += 25.0

        kural_tipi = "1h_dalga_gorsel"
        label = "1SAAT"
        if (close_curr_1h > hma20_1h.iloc[-1]) and (rsi_curr_1h > 50) and (plus_di_curr_1h > 25) and wave_breakout_1h:
          if kayit_guncelle(kural_tipi):
            tetiklenen_str.append(label)
            toplam_puan += 25.0

        kural_tipi = "deli_gitan_1h"
        label = "DELİ1H"
        if (close_curr_1h > hma20_1h.iloc[-1]) and (rvol_curr_1h >= 2.0) and wave_breakout_1h:
          if kayit_guncelle(kural_tipi):
            tetiklenen_str.append(label)
            toplam_puan += 35.0

        kural_tipi = "erken_hibrit_1h"
        label = "ERKEN"
        trend_1h_ok = (close_curr_1h > hma20_1h.iloc[-1])
        erken_tetik_15m = (rvol_curr_15 >= 2.0) and (75.0 <= konum_yuzde_15 <= 95.0) and sart_wave_15

        if trend_1h_ok and erken_tetik_15m:
          if kayit_guncelle(kural_tipi):
            tetiklenen_str.append(label)
            toplam_puan += 35.0

        if tetiklenen_str:
          if toplam_puan == 0:
            toplam_puan = 30.0

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
          print(f"  > {clean_ticker} inceleniyor... 🎯 Sinyal Yakalandı!")
        else:
          print(f"  > {clean_ticker} inceleniyor... [Temiz]")

      except Exception as e:
        print(f"  > Hata oluştu ({clean_ticker}): {e}")
        continue

  if toplanan_sinyaller:
    toplanan_sinyaller.sort(key=lambda x: x["puan"], reverse=True)
    zaman_str = datetime.now(TZ_TR).strftime('%d.%m %H:%M')

    birlesmis_dict = {}
    for item in toplanan_sinyaller:
      hisse = item['temiz_isim']
      if hisse not in birlesmis_dict:
        birlesmis_dict[hisse] = {
            'fiyat': item['fiyat'],
            'kazanc_yuzde': item['kazanc_yuzde'],
            'puan': item['puan'],
            'stratejiler': []
        }
      for strat in item['stratejiler']:
        if strat not in birlesmis_dict[hisse]['stratejiler']:
          birlesmis_dict[hisse]['stratejiler'].append(strat)
      if item['puan'] > birlesmis_dict[hisse]['puan']:
        birlesmis_dict[hisse]['puan'] = item['puan']

    # Kompakt Format: Karakter sınırını aşmamak için tek satırlık yapı
    mesaj_satirlari = [
        f"📊 BİST SİNYALLERİ ({len(birlesmis_dict)} Adet)",
        f"⏱️ {zaman_str}",
        "-" * 25
    ]

    sirali_hisseler = sorted(birlesmis_dict.items(), key=lambda x: x[1]['puan'], reverse=True)

    for hisse, veri in sirali_hisseler:
      kz = veri['kazanc_yuzde']
      getiri_str = f"+%{kz:.1f}" if kz >= 0 else f"%{kz:.1f}"
      strat_str = "/".join(veri['stratejiler'])
      
      # Her hisse için tek satırlık ultra kısa format
      satir = f"• **{hisse.upper()}**: ₺{veri['fiyat']:.2f} ({getiri_str}) | {strat_str}"
      mesaj_satirlari.append(satir)

    final_mesaj = "\n".join(mesaj_satirlari)
    send_ntfy(final_mesaj, "BIST Zirve Sinyaller")

  print("\nTüm Hisseler tarandı ve süreç tamamlandı.")

  simdi_kontrol = datetime.now(TZ_TR)
  saat = simdi_kontrol.hour
  dakika = simdi_kontrol.minute
  
  if os.environ.get("FORCE_RUN", "false").lower() == "true":
    performans_raporu_gonder("Manuel / Güncel")
  elif saat == 13 and 0 <= dakika <= 10:
    performans_raporu_gonder("Öğle (13:00)")
    time.sleep(600)
  elif saat == 18 and 0 <= dakika <= 15:
    performans_raporu_gonder("Gün Sonu")
    time.sleep(900)


if __name__ == "__main__":
  print("Tarama ve Performans Takip Sistemi başlatıldı...")
  run_scanner()
