/**
 * UniversalShield - Scam Detection Patterns
 */

const ScamPatterns = {
  RESUME_SCAMS: [
    /r[e3]sum[e3]\s*p[o0]l[i1]sh/gi,
    /cv\s*wr[i1]t[e3]r/gi,
    /r[e3]sum[e3]\s*[o0]pt[i1]m[i1]z/gi,
    /ATS\s*f[i1]x/gi,
    /attach\s*your\s*r[e3]sum[e3]/gi,
    /send\s*your\s*cv/gi,
    /quick\s*review/gi,
    /potential\s*opportunities/gi,
    /h[o0]ld[i1]ng\s*y[o0]u\s*b[a4]ck/gi,
    /g[e3]t\s*n[o0]t[i1]c[e3]d/gi,
    /pr[o0]v[e3]n\s*fr[a4]m[e3]w[o0]rk/gi,
    /LPS|ELITE|ST[A4]R|C[A4]R|WH[O0]/gi,
    /ATS\s*compl[i1]ant/gi,
    /m[o0]d[e3]rn\s*ATS/gi,
    /ATS\s*scr[e3][e3]n[i1]ng/gi,
    /f[i1]r[s5]t\s*scr[e3][e3]n[i1]ng/gi,
    /h[o0]n[e3]st\s*r[e3]c[o0]mm[e3]nd[a4]t[i1][o0]n/gi,
    /r[e3]sh[a4]p[e3]\s*[i1]t/gi,
    /l[a4]nd[i1]ng\s*[i1]nt[e3]rv[i1][e3]ws/gi,
    /w[o0]nt\s*m[a4]k[e3]\s*[i1]t\s*p[a4]st/gi,
    /TAS\s*compl[i1]ant/gi,
    /LPS|ELITE|ST[A4]R|C[A4]R|WH[O0]/gi,
    /proven\s*fr[a4]m[e3]w[o0]rks/gi,
    /ATS\s*s[y7]st[e3]ms/gi,
    /ATS\s*scr[e3][e3]n[i1]ng/gi,
    /h[i1]r[i1]ng\s*m[a4]n[a4]g[e3]r/gi
  ],
  BEHAVIORAL_FLAGS: [
    /k[i1]ndl[y7]\s*sh[a4]r[e3]/gi,
    /curr[e3]nt\s*l[o0]c[a4]t[i1][o0]n/gi,
    /y[e3][a4]r[s5]\s*[o0]f\s*[e3]xp[e3]r[i1][e3]nc[e3]/gi,
    /A:\s*Un[i1]t[e3]d\s*St[a4]t[e3][s5]/gi,
    /gmail\.com/gi
  ],
  URGENCY_WHATSAPP: [
    /wh[a4]ts[a4]pp/gi,
    /w\.h\.a\.t\.s/gi,
    /t\.me\//gi,
    /contact\s*me\s*v[i1][a4]/gi,
    /h[i1]r[i1]ng\s*[i1]mm[e3]d[i1][a4]t[e3]ly/gi,
    /urgent\s*response/gi,
    /limited\s*time/gi
  ],
  PAYMENT_CRYPTO: [
    /cr[y7]pt[o0]/gi,
    /p[a4][y7]m[e3]nt\s*f[e3][e3]/gi,
    /u[s5]dt/gi,
    /bi[t7]c[o0][i1]n/gi,
    /wire\s*transfer/gi,
    /gift\s*card/gi
  ],
  FINANCIAL_PHISHING: [
    /d[e3][s5][t7][i1]ny\s*m[a4][s5][t7][e3]rc[a4]rd/gi,
    /cr[e3]d[i1][t7]\s*l[i1]m[i1][t7]/gi,
    /inv[i1][t7][a4][t7][i1][o0]n\s*f[o0]r\s*cr[e3]d[i1][t7]/gi,
    /n[o0]\s*[s5][e3]cur[i1][t7][y7]\s*d[e3]p[o0][s5][i1][t7]/gi,
    /[a4]ppl[y7]\s*[t7][o0]d[a4][y7]/gi,
    /m[a4][s5][t7][e3]rc[a4]rd\s*[a4]ppl[i1]c[a4][t7][i1][o0]n/gi,
    /m[a4][s5][t7][e3]rc[a4]rd\s*gu[i1]d[e3]/gi
  ]
};

const RiskWeights = {
  RESUME_SCAMS: 40,
  BEHAVIORAL_FLAGS: 30,
  URGENCY_WHATSAPP: 50,
  PAYMENT_CRYPTO: 60,
  FINANCIAL_PHISHING: 70
};

// Export for use in content script
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ScamPatterns, RiskWeights };
}
