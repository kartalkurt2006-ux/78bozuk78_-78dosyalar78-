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
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] Erken Avcı (Hibrit TOPGUN) Sistemi Başlatıldı... (Manuel Mod: {is_manual_run})"
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
      close_curr_1h = 0.0
      hma20_1h_curr = 0.0

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

        is_1h_yakala_valid = False
        di_sarti_1h = False

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

            # RSI (14)
            delta_1h = close_1h.diff()
            gain_1h = (delta_1h.where(delta_1h > 0, 0)).rolling(14).mean()
            loss_1h = (-delta_1h.where(delta_1h < 0, 0)).rolling(14).mean()
            rs_1h = gain_1h / (loss_1h + 1e-10)
            rsi_curr_1h = (100 - (100 / (1 + rs_1h))).iloc[-1]
            son_rsi = rsi_curr_1h

            # MFI (14)
            mfi_1h = calculate_mfi(high_1h, low_1h, close_1h, volume_1h, 14)
            son_mfi = mfi_1h.iloc[-1]

            # +DI / -DI (14) Hesaplamaları (1h)
            up_move_1h = high_1h.diff()
            down_move_1h = -low_1h.diff()
            plus_dm_1h = up_move_1h.where((up_move_1h > down_move_1h) & (up_move_1h > 0), 0)
            minus_dm_1h = down_move_1h.where((down_move_1h > up_move_1h) & (down_move_1h > 0), 0)
            tr_1h = pd.concat([high_1h - low_1h, (high_1h - close_1h.shift()).abs(), (low_1h - close_1h.shift()).abs()], axis=1).max(axis=1)
            
            plus_di_1h = 100 * (plus_dm_1h.rolling(14).sum() / (tr_1h.rolling(14).sum() + 1e-10))
            minus_di_1h = 100 * (minus_dm_1h.rolling(14).sum() / (tr_1h.rolling(14).sum() + 1e-10))
            
            plus_di_curr_1h = plus_di_1h.iloc[-1]
            son_plus_di = plus_di_curr_1h

            # 1s DI Kesişim veya Üstünde Olma Şartı
            di_kesisim_1h = (plus_di_1h.iloc[-2] <= minus_di_1h.iloc[-2]) and (plus_di_1h.iloc[-1] > minus_di_1h.iloc[-1])
            di_ustunde_1h = plus_di_1h.iloc[-1] > minus_di_1h.iloc[-1]
            di_sarti_1h = di_kesisim_1h or di_ustunde_1h

            # RVOL (1h)
            rvol_curr_1h = (volume_1h / volume_1h.rolling(20).mean()).iloc[-1]
            son_rvol = rvol_curr_1h

            wave_res_1h = check_wave_margins(df_1h, lookback=3, threshold_multiplier=0.80)
            wave_breakout_1h = wave_res_1h[0]
            son_konum = wave_res_1h[1]

            hma20_1h = calculate_hma(close_1h, 20)
            hma20_1h_curr = hma20_1h.iloc[-1]

            # Strateji: 1 Saat Yakala
            if (close_curr_1h > hma20_1h_curr) and (rsi_curr_1h > 50) and (plus_di_curr_1h > 25) and wave_breakout_1h:
              is_1h_yakala_valid = True
              if kayit_guncelle("1h_dalga_gorsel"):
                tetiklenen_str.append("1 Saat Yakala")
                toplam_puan += 25.0

            # Strateji: DELİRDİ 1 Saat
            if (close_curr_1h > hma20_1h_curr) and (rvol_curr_1h >= 2.0) and wave_breakout_1h:
              if kayit_guncelle("deli_gitan_1h"):
                tetiklenen_str.append("DELİRDİ 1 Saat")
                toplam_puan += 35.0

        # ==========================================
        # 2. 15 DAKİKALIK VERİ ANALİZİ (TEHLİKELİ HİBRİT + TOPGUN)
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
            plus_di_curr_15 = (100 * (plus_dm_15m.rolling(14).sum() / (tr_15m.rolling(14).sum() + 1e-10))).iloc[-1]
            son_plus_di = max(son_plus_di, plus_di_curr_15)

            son_konum = max(son_konum, get_wave_position(df_15m))

            # Ichimoku Bulut Sınırları (15m)
            tenkan_9 = (high_15m.rolling(9).max() + low_15m.rolling(9).min()) / 2
            kijun_26 = (high_15m.rolling(26).max() + low_15m.rolling(26).min()) / 2
            senkou_span_a = (tenkan_9 + kijun_26) / 2
            senkou_span_b = (high_15m.rolling(52).max() + low_15m.rolling(52).min()) / 2
            kumo_ust = pd.concat([senkou_span_a, senkou_span_b], axis=1).max(axis=1)

            # Bulutun patlaması veya bulutun üstünde olması
            bulut_kirilimi = (close_15m.iloc[-2] <= kumo_ust.iloc[-2]) and (close_15m.iloc[-1] > kumo_ust.iloc[-1])
            bulut_ustunde = close_15m.iloc[-1] > kumo_ust.iloc[-1]
            ichimoku_hibrit_onay = bulut_kirilimi or bulut_ustunde

            hma20_15m = calculate_hma(close_15m, 20)
            is_above_hma20_15m = close_15m.iloc[-1] > hma20_15m.iloc[-1]

            # Strateji: TEHLİKELİ HİBRİT (1s Konum 0-60, 1s +DI/-DI Şartı, 1s HMA20 üstü fiyat & 15m Bulut Patlaması/Üstü, MFI>50, 15m +DI>30)
            konum_yuzde_1h_curr = get_wave_position(df_1h) if not df_1h.empty else get_wave_position(df_15m)
            if (0.0 <= konum_yuzde_1h_curr <= 60.0) and di_sarti_1h and (close_curr_1h > hma20_1h_curr) and (mfi_curr_15 > 50.0) and (plus_di_curr_15 > 30.0) and ichimoku_hibrit_onay:
              if kayit_guncelle("dip_hibrit"):
                tetiklenen_str.append("TEHLİKELİ HİBRİT")
                toplam_puan += 30.0

            # Strateji: TOPGUN (1 Saat Yakala kuralları + 15m Ichimoku + MFI>50 + +DI>25 + HMA20 üstü fiyat)
            if is_1h_yakala_valid and ichimoku_hibrit_onay and (plus_di_curr_15 > 25.0) and (mfi_curr_15 > 50.0) and is_above_hma20_15m:
              if kayit_guncelle("topgun_strategy"):
                tetiklenen_str.append("TOPGUN")
                toplam_puan += 45.0

        # ==========================================
        # 3. SÜPER 15 CROSS MODÜLÜ (PASİFİZE EDİLDİ)
        # ==========================================
        if False:
          pass

        # ==========================================
        # 4. 🛡️ DENİZ DALGASI MODÜLÜ (PASİFİZE EDİLDİ)
        # ==========================================
        if False:
          pass

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
          prefix = "👑🚨 DİKKAT: 1S ÇİFTE ALARM 🚨👑"
        elif len(item['stratejiler']) >= 3:
          prefix = "🚀🚀🚀 Hisse:"
        else:
          prefix = "📌 Hisse:"
        
        mesaj_satirlari.append(f"{prefix} 🟦 {item['temiz_isim']} 🟦 | Fiyat: ₺{item['fiyat']:.2f}")
        
        for strat in item['stratejiler']:
          strat_upper = strat.upper()
          if "TOPGUN" in strat_upper:
            mesaj_satirlari.append(f"• 🦅🐴🦅 {strat} (RSI:{item['rsi']:.1f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | Konum:%{item['konum']:.1f})")
          elif "TEHLİKELİ HİBRİT" in strat_upper:
            mesaj_satirlari.append(f"• 🟢🟢🟢 {strat} (MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | Konum:%{item['konum']:.1f})")
          elif "DELİRDİ" in strat_upper and "1 SAAT" in strat_upper:
            mesaj_satirlari.append(f"• 💥💥💥 {strat} (RVOL:{item['rvol']:.2f} | MFI:{item['mfi']:.1f} | +DI:{item['plus_di']:.1f} | Konum:%{item['konum']:.1f})")
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
