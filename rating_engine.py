from analyze_song import analyze_song
import numpy as np

def rate_song(filepath):
    """
    Evalúa la calidad técnica de una canción basándose en múltiples métricas.
    Devuelve un puntaje de 0-100 y un análisis detallado.
    """
    try:
        analysis = analyze_song(filepath)
        if 'error' in analysis:
            return {
                'score': 0,
                'error': analysis['error'],
                'details': None
            }

        score = 0
        max_score = 0
        details = []

        # 1. Evaluación de dinámica (20 puntos máximo)
        dynamics = analysis.get('dynamics', {})
        if dynamics:
            max_score += 20
            # Loudness (-14 LUFS es estándar para streaming)
            if dynamics.get('lufs', -np.inf) >= -14:
                score += 5
                details.append("✅ Loudness óptimo para streaming")
            else:
                details.append("⚠️ Loudness bajo para streaming")

            # Crest factor (2-4 es ideal)
            crest = dynamics.get('crest_factor', 0)
            if 2 <= crest <= 4:
                score += 5
                details.append(f"✅ Crest factor ideal ({crest:.1f})")
            else:
                details.append(f"⚠️ Crest factor fuera de rango ({crest:.1f})")

            # Clipping
            clipping = dynamics.get('clipping_ratio', 1)
            if clipping < 0.001:
                score += 5
                details.append("✅ Sin clipping detectable")
            elif clipping < 0.01:
                score += 3
                details.append(f"⚠️ Clipping mínimo ({clipping*100:.2f}%)")
            else:
                details.append(f"❌ Clipping excesivo ({clipping*100:.2f}%)")

            # RMS (nivel promedio)
            rms = dynamics.get('rms', 0)
            if 0.05 <= rms <= 0.1:
                score += 5
                details.append(f"✅ Nivel RMS óptimo ({rms:.4f})")
            else:
                details.append(f"⚠️ Nivel RMS fuera de rango ideal ({rms:.4f})")

        # 2. Evaluación de ruido (20 puntos máximo)
        noise_ratio = analysis.get('noise_ratio', 1)
        max_score += 20
        if noise_ratio < 0.1:
            score += 20
            details.append("✅ Relación señal/ruido excelente")
        elif noise_ratio < 0.2:
            score += 15
            details.append("⚠️ Ruido detectable pero aceptable")
        elif noise_ratio < 0.3:
            score += 10
            details.append("⚠️ Ruido notable")
        else:
            details.append("❌ Ruido excesivo")

        # 3. Evaluación de afinación vocal (20 puntos máximo)
        tuning = analysis.get('tuning', {})
        if tuning and tuning.get('confidence', 0) > 0.6:
            max_score += 20
            conf = tuning.get('confidence', 0)
            if conf > 0.8:
                score += 20
                details.append(f"✅ Afinación vocal precisa (confianza: {conf:.2f})")
            elif conf > 0.6:
                score += 15
                details.append(f"⚠️ Afinación vocal aceptable (confianza: {conf:.2f})")
        else:
            details.append("❌ Afinación vocal no detectable o baja confianza")

        # 4. Balance de frecuencias (20 puntos máximo)
        bands = analysis.get('frequency_bands', {})
        if bands:
            max_score += 20
            balance_score = 0
            # Verificar distribución equilibrada
            total = sum(bands.values())
            if total > 0:
                lows = (bands['sub_bass'] + bands['bass']) / total
                mids = (bands['low_mids'] + bands['mids']) / total
                highs = (bands['highs'] + bands['air']) / total

                if 0.2 < lows < 0.4 and 0.3 < mids < 0.5 and 0.2 < highs < 0.4:
                    balance_score = 20
                    details.append("✅ Balance de frecuencias ideal")
                elif (abs(lows - 0.3) < 0.15 and abs(mids - 0.4) < 0.15 and abs(highs - 0.3) < 0.15):
                    balance_score = 15
                    details.append("⚠️ Balance de frecuencias aceptable")
                else:
                    details.append("❌ Desbalance frecuencial detectado")

                score += balance_score

        # 5. Métricas adicionales (20 puntos máximo)
        max_score += 20
        # Duración (ejemplo: entre 2 y 10 minutos)
        duration = analysis.get('duration', 0)
        if 120 <= duration <= 600:
            score += 5
            details.append(f"✅ Duración adecuada ({duration//60}:{duration%60:02d})")
        else:
            details.append(f"⚠️ Duración atípica ({duration//60}:{duration%60:02d})")

        # Puedes añadir más criterios aquí

        # Normalizar puntaje
        final_score = round((score / max_score) * 5, 2) if max_score > 0 else 0.0

        return {
            'score': final_score,
            'details': details,
            'raw_analysis': analysis
        }

    except Exception as e:
        return {
            'score': 0,
            'error': str(e),
            'details': None
        }