"""Build deck/deploy-with-ocm-with-confidence.pptx on top of the official CNCF KubeCon NA 2026 template.

Usage: python3 hack/build-pptx.py <template.pptx> <out.pptx>

Keeps the template's masters, layouts and artwork, drops its sample slides, and adds
seven slides whose diagrams are native, editable PowerPoint shapes. Standard library only.
"""
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

TEMPLATE, OUT = Path(sys.argv[1]), Path(sys.argv[2])
BUILD = Path(tempfile.mkdtemp(prefix="pptx-build-"))

# Palette from the template theme
NAVY, BLUE, GREEN, MAG = "052243", "113E82", "2E9C68", "D62293"
LBLUE, PINK, LGREEN, PANEL = "E3F6FF", "FBE3F1", "E6F6EF", "F3F7FC"
MUTED, LINE, WHITE, PALE = "4F607A", "D6DEEA", "FFFFFF", "ADC5EF"
MONO = "Courier New"


def emu(inches):
    return int(round(inches * 914400))


_ids = [100]


def nid():
    _ids[0] += 1
    return _ids[0]


_anim = []  # (click step, shape id) for the slide being built


def _rec(i, step):
    if step is not None:
        _anim.append((step, i))
    return i


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(text, sz=14, b=False, color=NAVY, font="Arial", i=False):
    attrs = f' lang="en-US" sz="{int(sz*100)}" b="{1 if b else 0}" i="{1 if i else 0}" dirty="0"'
    return (f"<a:r><a:rPr{attrs}><a:solidFill><a:srgbClr val=\"{color}\"/></a:solidFill>"
            f"<a:latin typeface=\"{font}\"/><a:cs typeface=\"{font}\"/></a:rPr><a:t>{esc(text)}</a:t></a:r>")


def para(runs, algn="l", after=0, before=0, sz=14):
    if isinstance(runs, str):
        runs = run(runs, sz=sz)
    elif isinstance(runs, list):
        runs = "".join(runs)
    sp = ""
    if before:
        sp += f'<a:spcBef><a:spcPts val="{int(before*100)}"/></a:spcBef>'
    if after:
        sp += f'<a:spcAft><a:spcPts val="{int(after*100)}"/></a:spcAft>'
    return f'<a:p><a:pPr algn="{algn}">{sp}</a:pPr>{runs}<a:endParaRPr lang="en-US" sz="{int(sz*100)}"/></a:p>'


def body(paras, anchor="ctr", ins=0.05, wrap="square"):
    i = emu(ins)
    return (f'<p:txBody><a:bodyPr wrap="{wrap}" lIns="{i}" tIns="{i}" rIns="{i}" bIns="{i}" '
            f'anchor="{anchor}" anchorCtr="0"/><a:lstStyle/>{"".join(paras)}</p:txBody>')


def shape(x, y, w, h, prst="rect", fill=None, line=None, lw=1.0, dash=None, paras=None,
          anchor="ctr", ins=0.05, adj=None, name="Shape", step=None):
    geom = f'<a:prstGeom prst="{prst}"><a:avLst>'
    if adj is not None:
        geom += f'<a:gd name="adj" fmla="val {adj}"/>'
    geom += "</a:avLst></a:prstGeom>"
    f = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    if line:
        d = f'<a:prstDash val="{dash}"/>' if dash else ""
        ln = f'<a:ln w="{int(lw*12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>{d}</a:ln>'
    else:
        ln = "<a:ln><a:noFill/></a:ln>"
    tx = body(paras, anchor, ins) if paras else body([para("")], anchor, ins)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_rec(nid(), step)}" name="{esc(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'{geom}{f}{ln}</p:spPr>{tx}</p:sp>')


def text(x, y, w, h, paras, anchor="ctr", ins=0.0, name="Text", step=None):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_rec(nid(), step)}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>{body(paras, anchor, ins)}</p:sp>')


def connector(x1, y1, x2, y2, color=NAVY, lw=1.5, arrow=True, dash=None, cap=None, name="Connector", step=None):
    flip = ""
    if x2 < x1:
        flip += ' flipH="1"'
    if y2 < y1:
        flip += ' flipV="1"'
    d = f'<a:prstDash val="{dash}"/>' if dash else ""
    capattr = f' cap="{cap}"' if cap else ""
    tail = '<a:tailEnd type="triangle" w="med" len="med"/>' if arrow else ""
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{_rec(nid(), step)}" name="{esc(name)}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{flip}><a:off x="{emu(min(x1,x2))}" y="{emu(min(y1,y2))}"/>'
            f'<a:ext cx="{emu(abs(x2-x1))}" cy="{emu(abs(y2-y1))}"/></a:xfrm>'
            f'<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{int(lw*12700)}"{capattr}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{d}{tail}</a:ln>'
            f'</p:spPr></p:cxnSp>')


def title_ph(runs, x=None, y=None, w=None, h=None, sz=28, ph_type="title", idx=None, anchor="ctr", b=True, color=None):
    xfrm = ""
    if x is not None:
        xfrm = f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
    idxattr = f' idx="{idx}"' if idx is not None else ""
    if isinstance(runs, str):
        fill = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else ""
        runs = (f'<a:r><a:rPr lang="en-US" sz="{int(sz*100)}" b="{1 if b else 0}" dirty="0">{fill}'
                f'<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>{esc(runs)}</a:t></a:r>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{nid()}" name="Title"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="{ph_type}"{idxattr}/></p:nvPr></p:nvSpPr>'
            f'<p:spPr>{xfrm}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr anchorCtr="0" anchor="{anchor}" bIns="0" lIns="0" rIns="0" tIns="0" wrap="square"><a:normAutofit/></a:bodyPr>'
            f'<a:lstStyle/><a:p><a:pPr algn="l"/>{runs}<a:endParaRPr lang="en-US" sz="{int(sz*100)}"/></a:p></p:txBody></p:sp>')


def slidenum_ph(n):
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Slide Number"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="sldNum" idx="12"/></p:nvPr></p:nvSpPr>'
            '<p:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/>'
            '<a:p><a:pPr algn="r"/><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum"><a:rPr lang="en-US" sz="1000"/>'
            '<a:t>%d</a:t></a:fld><a:endParaRPr lang="en-US" sz="1000"/></a:p></p:txBody></p:sp>') % (nid(), n)


def timing_xml():
    """Click-triggered fade-in builds: one click per step, shapes in a step appear together."""
    if not _anim:
        return ""
    cid = [2]

    def c():
        cid[0] += 1
        return cid[0]

    clicks = []
    for step in sorted({st for st, _ in _anim}):
        ids = [i for st, i in _anim if st == step]
        outer, inner = c(), c()
        effs = []
        for k, sid in enumerate(ids):
            node = "clickEffect" if k == 0 else "withEffect"
            e1, e2, e3 = c(), c(), c()
            effs.append(
                f'<p:par><p:cTn id="{e1}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="{node}">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                f'<p:set><p:cBhvr><p:cTn id="{e2}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                f'<p:to><p:strVal val="visible"/></p:to></p:set>'
                f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{e3}" dur="400"/>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
                f'</p:childTnLst></p:cTn></p:par>')
        clicks.append(
            f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            + "".join(effs) + '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    bld = "".join(f'<p:bldP spid="{i}" grpId="0" animBg="1"/>' for _, i in _anim)
    return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            + "".join(clicks) +
            '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            '</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>' + bld + '</p:bldLst></p:timing>')


def slide_xml(shapes):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + "".join(shapes) +
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>' + timing_xml() + '</p:sld>')


def table(x, y, col_w, rows, header_h=0.34, row_h=0.38):
    """rows: list of (cells, fill); cells: list of paragraph xml strings."""
    grid = "".join(f'<a:gridCol w="{emu(w)}"/>' for w in col_w)
    trs = []
    for ri, (cells, fill) in enumerate(rows):
        h = header_h if ri == 0 else row_h
        tcs = []
        for c in cells:
            f = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
            tcs.append(f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>{c}</a:txBody>'
                       f'<a:tcPr marL="{emu(0.1)}" marR="{emu(0.1)}" marT="{emu(0.04)}" marB="{emu(0.04)}" anchor="ctr">'
                       f'<a:lnL><a:noFill/></a:lnL><a:lnR><a:noFill/></a:lnR><a:lnT><a:noFill/></a:lnT>'
                       f'<a:lnB w="12700"><a:solidFill><a:srgbClr val="{LINE}"/></a:solidFill></a:lnB>{f}</a:tcPr></a:tc>')
        trs.append(f'<a:tr h="{emu(h)}">{"".join(tcs)}</a:tr>')
    total_h = header_h + row_h * (len(rows) - 1)
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{nid()}" name="Table"/>'
            f'<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(sum(col_w))}" cy="{emu(total_h)}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl><a:tblPr/>'
            f'<a:tblGrid>{grid}</a:tblGrid>{"".join(trs)}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>')


def callout(txt_runs, y=4.05, h=0.75, sz=13):
    return shape(0.5, y, 9.0, h, prst="roundRect", fill=LBLUE, adj=8000, ins=0.18,
                 paras=[para(txt_runs, sz=sz)], name="Callout")


def T1(sz=14):
    return run("T1", sz=sz, b=True, color=BLUE)


def T2(sz=14):
    return run("T2", sz=sz, b=True, color=GREEN)


# ----------------------------------------------------------------------------- slides

def slide_title():
    return [
        text(0.34, 1.02, 9.3, 0.3, [para([run("OCM Project Lightning Talk  ·  KubeCon + CloudNativeCon North America 2026  ·  Salt Lake City",
                                              sz=12, color=MUTED)])], anchor="b", name="Event"),
        title_ph("Hub → managed cluster in how many milliseconds?", 0.34, 1.88, 8.76, 1.02, sz=30, ph_type="ctrTitle"),
        title_ph("Suvaansh Kumar  ·  Software Engineer at Guidewire  ·  Open Cluster Management maintainer",
                 0.34, 2.92, 8.76, 0.38, sz=14, ph_type="subTitle", idx=1, b=False),
    ]


def slide_usecase(n):
    S = [title_ph("At Guidewire: one hub cluster, many regions"), slidenum_ph(n)]
    S.append(shape(0.5, 1.45, 2.4, 2.1, prst="roundRect", fill=LBLUE, line=BLUE, lw=1.5, adj=8000, paras=[
        para([run("Hub cluster", sz=18, b=True)], algn="ctr", after=2),
        para([run("us-east", sz=12, color=MUTED)], algn="ctr", after=14),
        para([run("Teams apply", sz=11)], algn="ctr"),
        para([run("workloads here", sz=11)], algn="ctr"),
    ], name="Hub"))
    def cluster(name, cy, fill, ln, step=None):
        return shape(7.0, cy, 2.5, 0.8, prst="roundRect", fill=fill, line=ln, lw=1.25, adj=10000, paras=[
            para([run(name, sz=14, b=True)], algn="ctr"),
            para([run("managed cluster", sz=10, color=MUTED)], algn="ctr"),
        ], name=name, step=step)

    for name, cy in (("us-west", 1.3), ("ap-south", 2.3), ("eu-west", 3.3)):
        S.append(cluster(name, cy, PANEL, MUTED))
    # click 1: workloads go out
    for y1, y2 in ((2.0, 1.7), (2.5, 2.7), (3.0, 3.7)):
        S.append(connector(2.9, y1, 7.0, y2, color=MUTED, lw=1.5, step=1))
    for ly in (1.55, 2.3, 3.05):
        S.append(text(4.15, ly, 1.6, 0.22, [para([run("workload", sz=9, color=MUTED)], algn="ctr")], anchor="b", step=1))
    # click 2: the questions
    S.append(connector(2.9, 3.0, 7.0, 3.7, color=MAG, lw=1.5, step=2))
    S.append(cluster("eu-west", 3.3, PINK, MAG, step=2))
    for ly, q in ((1.55, "? ms"), (2.3, "? ms"), (3.05, "never arrived?")):
        S.append(text(4.15, ly + 0.3, 1.6, 0.3, [para([run(q, sz=14, b=True, color=MAG)], algn="ctr")], anchor="t", step=2))
    S.append(callout([run("The hub knows the workload was ", sz=13), run("accepted", sz=13, b=True),
                      run(". It can't tell us ", sz=13), run("how long", sz=13, b=True),
                      run(" it took to land in each region, or ", sz=13), run("whether it landed at all", sz=13, b=True),
                      run(".", sz=13)]))
    _anim.append((2, _ids[0]))  # the callout shape just created
    return S


def slide_flow(n):
    S = [title_ph("Two timestamps, one key"), slidenum_ph(n)]
    S.append(shape(6.2, 1.12, 3.4, 0.3, prst="roundRect", line=GREEN, lw=1, adj=50000, ins=0.02, paras=[
        para([run("T2 log: in ", sz=10, color=GREEN), run("OCM v1.4", sz=10, b=True, color=GREEN),
              run(", contributed by Guidewire", sz=10, color=GREEN)], algn="ctr")], name="Credit", step=4))
    # user
    S.append(shape(0.45, 1.72, 0.5, 0.5, prst="ellipse", fill=PANEL, line=NAVY, lw=1.25, name="User head"))
    S.append(shape(0.33, 2.27, 0.74, 0.34, prst="roundRect", fill=PANEL, line=NAVY, lw=1.25, adj=50000, name="User body"))
    S.append(text(0.2, 2.64, 1.0, 0.24, [para([run("User", sz=11)], algn="ctr")]))
    # hub
    S.append(shape(1.3, 1.5, 3.1, 1.8, prst="roundRect", fill=LBLUE, line=BLUE, lw=1.5, adj=6000, name="Hub"))
    S.append(text(1.45, 1.54, 2.9, 0.28, [para([run("Hub cluster", sz=13, b=True), run("  ·  us-east", sz=12, color=MUTED)])]))
    S.append(shape(1.5, 1.85, 2.7, 0.5, prst="roundRect", fill=WHITE, line=PALE, lw=1, adj=10000,
                   paras=[para([run("kube-apiserver", sz=12)], algn="ctr")], name="apiserver"))
    S.append(connector(2.85, 2.35, 2.85, 2.6, color=PALE, lw=1.5, arrow=False))
    S.append(shape(1.5, 2.6, 2.7, 0.5, prst="roundRect", fill=WHITE, line=PALE, lw=1, adj=10000,
                   paras=[para([run("Admission webhook", sz=12)], algn="ctr")], name="webhook"))
    # managed
    S.append(shape(6.2, 1.5, 3.3, 1.8, prst="roundRect", fill=LGREEN, line=GREEN, lw=1.5, adj=6000, name="Managed"))
    S.append(text(6.35, 1.54, 3.1, 0.28, [para([run("Managed cluster", sz=13, b=True), run("  ·  ap-south", sz=12, color=MUTED)])]))
    S.append(shape(6.45, 2.3, 2.8, 0.5, prst="roundRect", fill=WHITE, line="A9DCC6", lw=1, adj=10000,
                   paras=[para([run("Work agent", sz=12)], algn="ctr")], name="agent"))
    # flows
    S.append(connector(1.1, 2.1, 1.5, 2.1, color=NAVY, lw=1.5, step=1))
    S.append(text(0.95, 1.86, 0.7, 0.22, [para([run("apply", sz=9)], algn="ctr")], anchor="b", step=1))
    S.append(connector(4.2, 2.1, 6.45, 2.55, color=NAVY, lw=1.5, step=3))
    S.append(text(4.55, 1.86, 1.6, 0.24, [para([run("workload", sz=10)], algn="ctr")], anchor="b", step=3))
    S.append(text(4.55, 2.62, 1.6, 0.24, [para([run("via watch", sz=9, color=MUTED)], algn="ctr")], anchor="t", step=3))
    # T1 / T2
    S.append(connector(2.85, 3.1, 2.85, 3.6, color=BLUE, lw=1.5, step=2))
    S.append(shape(1.3, 3.62, 3.1, 0.78, prst="roundRect", fill=WHITE, line=BLUE, lw=1.5, adj=8000, ins=0.12, anchor="t", paras=[
        para([run("T1", sz=13, b=True, color=BLUE), run("   hub webhook log", sz=10, color=MUTED)], after=2),
        para([run("ManifestWork name · managed cluster · generation · UTC timestamp", sz=9)])], name="T1 log", step=2))
    S.append(connector(7.85, 2.8, 7.85, 3.6, color=GREEN, lw=1.5, step=4))
    S.append(shape(6.2, 3.62, 3.3, 0.78, prst="roundRect", fill=WHITE, line=GREEN, lw=1.5, adj=8000, ins=0.12, anchor="t", paras=[
        para([run("T2", sz=13, b=True, color=GREEN), run("   work agent log", sz=10, color=MUTED)], after=2),
        para([run("ManifestWork name · managed cluster · generation · UTC timestamp", sz=9)])], name="T2 log", step=4))
    # result
    S.append(connector(3.3, 4.4, 3.65, 4.68, color=BLUE, lw=1.5, step=5))
    S.append(connector(7.1, 4.4, 6.75, 4.68, color=GREEN, lw=1.5, step=5))
    S.append(shape(3.7, 4.42, 3.0, 0.54, prst="roundRect", fill=NAVY, adj=8000, ins=0.04, paras=[
        para([run("Match on cluster + ManifestWork + generation", sz=8, color=PALE)], algn="ctr", after=1),
        para([run("T2 − T1 = 434 ms", sz=16, b=True, color=WHITE)], algn="ctr")], name="Result", step=5))
    return S


def code_box(x, y, label_runs, lines, ts_color):
    S = [text(x, 1.24, 4.5, 0.25, [para(label_runs)], anchor="b")]
    paras = []
    for i, ln in enumerate(lines):
        if i == len(lines) - 1:
            k, v = ln.split("=", 1)
            paras.append(para([run(k + "=", sz=11, font=MONO), run(v, sz=11, b=True, color=ts_color, font=MONO)], after=3))
        else:
            paras.append(para([run(ln, sz=11, font=MONO)], after=3))
    S.append(shape(x, 1.52, 4.5, 1.25, prst="roundRect", fill=PANEL, line=LINE, lw=1, adj=6000, ins=0.18,
                   anchor="ctr", paras=paras, name="Code"))
    return S


def slide_match(n):
    S = [title_ph("Match the two logs"), slidenum_ph(n)]
    S += code_box(0.34, 1.52, [T1(11), run("   hub cluster admission webhook", sz=10, b=True, color=MUTED)],
                  ["workload/ManifestWork=workload-1", "managed cluster=ap-south", "generation=2", "timestamp=08:05:00.200 UTC"], BLUE)
    S += code_box(5.16, 1.52, [T2(11), run("   managed cluster work agent", sz=10, b=True, color=MUTED)],
                  ["workload/ManifestWork=workload-1", "managed cluster=ap-south", "generation=2", "timestamp=08:05:00.634 UTC"], GREEN)

    def hdr(t):
        return para([run(t.upper(), sz=9, b=True, color=MUTED)])

    def mono(t, b=False, color=NAVY):
        return para([run(t, sz=11, b=b, color=color, font=MONO)])

    rows = [
        ([hdr("Managed cluster"), hdr("Workload / ManifestWork"), hdr("Generation"), hdr("Latency")], None),
        ([mono("ap-south"), mono("workload-1"), mono("1"), mono("912 ms")], None),
        ([mono("ap-south"), mono("workload-1"), mono("2"), mono("434 ms", b=True)], None),
        ([mono("ap-south"), mono("workload-1"), mono("3"), mono("NEVER ARRIVED", b=True, color=MAG)], PINK),
    ]
    S.append(table(0.34, 3.0, [2.33, 2.33, 2.33, 2.33], rows))
    S.append(text(0.34, 4.55, 6, 0.25, [para([run("Example output from the sample logs in examples/.", sz=9, color=MUTED)])], anchor="t"))
    return S


def slide_never(n):
    S = [title_ph("Never arrived? Look for the missing T2"), slidenum_ph(n)]
    S.append(text(0.5, 1.38, 2.8, 0.25, [para([run("HUB CLUSTER LOG", sz=10, b=True, color=MUTED)], algn="ctr")], anchor="b"))
    S.append(text(6.7, 1.38, 2.8, 0.25, [para([run("MANAGED CLUSTER LOG", sz=10, b=True, color=MUTED)], algn="ctr")], anchor="b"))
    S.append(shape(0.5, 1.7, 2.8, 1.0, prst="roundRect", fill=LBLUE, line=BLUE, lw=2, adj=8000, ins=0.18, paras=[
        para([run("T1", sz=18, b=True, color=BLUE), run("  ·  eu-west", sz=15)], after=3),
        para([run("08:05:00.210 UTC", sz=12, color=MUTED, font=MONO)])], name="T1"))
    S.append(shape(6.7, 1.7, 2.8, 1.0, prst="roundRect", fill=WHITE, line="9AA8BD", lw=1.5, dash="dash", adj=8000, paras=[
        para([run("T2 ?", sz=16, color="9AA8BD")], algn="ctr")], name="T2 pending"))
    # click 1: waiting, the timeout runs
    S.append(connector(3.35, 2.2, 4.45, 2.2, color=MUTED, lw=2, arrow=False, step=1))
    S.append(text(4.6, 2.0, 2.0, 0.4, [para([run("waiting for T2…", sz=14, color=MUTED)])], step=1))
    S.append(connector(3.35, 3.25, 9.5, 3.25, color=LINE, lw=6, arrow=False, cap="rnd", step=1))
    S.append(text(3.35, 3.36, 1.5, 0.25, [para([run("timeout", sz=10, color=MUTED)])], anchor="t", step=1))
    S.append(text(8.0, 3.36, 1.5, 0.25, [para([run("2 min", sz=10, color=MUTED)], algn="r")], anchor="t", step=1))
    # click 2: timeout passes with no T2
    S.append(connector(3.35, 2.2, 4.45, 2.2, color=MAG, lw=2, arrow=False, step=2))
    S.append(shape(4.5, 1.98, 2.3, 0.44, fill=WHITE, ins=0.0, paras=[
        para([run("✕  never arrived", sz=16, b=True, color=MAG)])], anchor="ctr", name="Never arrived", step=2))
    S.append(connector(3.35, 3.25, 9.5, 3.25, color=MAG, lw=6, arrow=False, cap="rnd", step=2))
    S.append(shape(6.7, 1.7, 2.8, 1.0, prst="roundRect", fill=PINK, line=MAG, lw=2, adj=8000, paras=[
        para([run("No T2", sz=18, b=True, color=MAG)], algn="ctr")], name="No T2", step=2))
    S.append(callout([T1(14), run(" with no ", sz=14), T2(14), run(" after a timeout: the workload ", sz=14),
                      run("never arrived", sz=14, b=True), run(".", sz=14)], sz=14))
    _anim.append((2, _ids[0]))  # the callout shape just created
    return S


def slide_steps(n):
    S = [title_ph("Works with any observability tool"), slidenum_ph(n)]
    rows = [
        [run("Find", sz=14, b=True), run(" the hub cluster log (", sz=14), T1(), run(") and the managed cluster log (", sz=14), T2(), run(")", sz=14)],
        [run("Match", sz=14, b=True), run(" them on managed cluster name + ManifestWork name + generation", sz=14)],
        [run("Subtract", sz=14, b=True), run(":  ", sz=14), T2(), run(" − ", sz=14), T1(), run(" = latency", sz=14)],
        [run("Catch", sz=14, b=True), run(" the missing ", sz=14), T2(), run(": none after a timeout = ", sz=14), run("never arrived", sz=14, b=True, color=MAG)],
    ]
    for i, runs in enumerate(rows):
        y = 1.4 + i * 0.82
        S.append(shape(0.5, y, 9.0, 0.68, prst="roundRect", fill=PANEL, line=LINE, lw=1, adj=10000, name=f"Step {i+1}"))
        S.append(shape(0.72, y + 0.14, 0.4, 0.4, prst="ellipse", fill=NAVY, ins=0,
                       paras=[para([run(str(i + 1), sz=14, b=True, color=WHITE)], algn="ctr")], name=f"Number {i+1}"))
        S.append(text(1.3, y, 8.0, 0.68, [para(runs)]))
    return S


def slide_close():
    return [
        title_ph("Thank you", 0.34, 1.92, 9.32, 0.68, sz=36),
        text(0.34, 2.62, 9.32, 0.72, [
            para([run("Running into issues? Reach us in ", sz=12, color=WHITE), run("#open-cluster-mgmt", sz=12, b=True, color=WHITE),
                  run(" on Kubernetes Slack", sz=12, color=WHITE)], after=2),
            para([run("Slides, scripts and sample logs: ", sz=12, color=WHITE),
                  run("github.com/suvaanshkumar/Kubecon-na-2026-ocm-lt", sz=12, b=True, color=WHITE)], after=2),
            para([run("Thanks to the Open Cluster Management maintainers and contributors.", sz=12, color=WHITE)]),
        ], anchor="t"),
    ]


NOTES = {
    1: ["Starts at 0:00.",
        "I'm Suvaansh, a software engineer at Guidewire and an Open Cluster Management maintainer. Five minutes on one question: did my workload land?"],
    2: ["Starts at 0:20. Two clicks.",
        "Open: At Guidewire we run one OCM hub cluster and managed clusters in several regions.",
        "Click 1: Teams apply a workload on the hub cluster and OCM sends it to every region.",
        "Click 2: The hub cluster knows the workload was accepted. It can't tell us how long it took to land in us-west or ap-south, or whether it reached eu-west at all. Until recently OCM had no signal from the managed cluster for this."],
    3: ["Starts at 0:55. Five clicks.",
        "Click 1: A user applies a workload/ManifestWork on the hub cluster.",
        "Click 2: The hub cluster's webhook sends a log with the workload/ManifestWork name, generation and a UTC timestamp. That's T1. Both sides log in UTC, so we can compare them directly.",
        "Click 3: The work agent on the managed cluster picks it up over its watch.",
        "Click 4: It applies the workload and sends the same kind of log, with its own timestamp. That's T2. This managed cluster log ships in OCM 1.4; we contributed it upstream.",
        "Click 5: Your observability tool matches the two logs and subtracts. Nothing on the clusters does the math."],
    4: ["Starts at 1:50.",
        "One workload on one managed cluster, ap-south. The hub cluster log and the managed cluster log carry the same workload name, managed cluster and generation. Generation 1, the first rollout, took 912 milliseconds. Generation 2 was a smaller change and took 434. Generation 3 has a T1 but no T2: it never arrived."],
    5: ["Starts at 2:35. Two clicks.",
        "Open: Here's a workload for eu-west. The hub cluster logged its T1.",
        "Click 1: But no T2. We give it a timeout.",
        "Click 2: Timeout passes, still no T2. That workload never arrived. That's the whole check: a T1 with no T2.",
        "Q&A backup: no T2 can also mean the managed cluster's logs aren't reaching your observability tool, so check the ManifestWork status on the hub to confirm. A T2 that says apply failed means it arrived but didn't apply."],
    6: ["Starts at 3:25.",
        "None of this is tied to a vendor. Find the two logs, match them on managed cluster name, workload/ManifestWork name and generation, subtract. And catch the missing T2: none after a timeout means it never arrived. Any observability tool can do that."],
    7: ["Starts at 4:00.",
        "If you run into any issues, reach us in #open-cluster-mgmt on Kubernetes Slack. Thank you."],
}


# ----------------------------------------------------------------------------- build

CT = "[Content_Types].xml"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
LAYOUT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
NOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
NOTES_MASTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster"
XMLNS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
         'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
         'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')


def add_notes(n, lines):
    """Attach speaker notes to slide n using the template's notes master."""
    notes = BUILD / "ppt" / "notesSlides"
    (notes / "_rels").mkdir(parents=True, exist_ok=True)
    paras = "".join(f'<a:p><a:r><a:rPr lang="en-US" dirty="0"/><a:t>{esc(t)}</a:t></a:r></a:p>' for t in lines)
    (notes / f"notesSlide{n}.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:notes {XMLNS}><p:cSld><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph idx="2" type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>'
        '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr><p:ph idx="1" type="body"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>'
        '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>', encoding="utf-8")
    (notes / "_rels" / f"notesSlide{n}.xml.rels").write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Relationships xmlns="{REL_NS}"><Relationship Id="rId1" Type="{NOTES_MASTER_REL}" Target="../notesMasters/notesMaster1.xml"/>'
        f'<Relationship Id="rId2" Type="{SLIDE_REL}" Target="../slides/slide{n}.xml"/></Relationships>')
    ct = BUILD / CT
    ct.write_text(ct.read_text().replace("</Types>",
        f'<Override PartName="/ppt/notesSlides/notesSlide{n}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>'))
    rels = BUILD / "ppt" / "slides" / "_rels" / f"slide{n}.xml.rels"
    rels.write_text(rels.read_text().replace("</Relationships>",
        f'<Relationship Id="rId2" Type="{NOTES_REL}" Target="../notesSlides/notesSlide{n}.xml"/></Relationships>'))


def remove_template_slides():
    """Delete every sample slide (and its notes) from the unpacked template."""
    for f in list((BUILD / "ppt" / "slides").glob("slide*.xml")) + list((BUILD / "ppt" / "slides" / "_rels").glob("*.rels")):
        f.unlink()
    notes = BUILD / "ppt" / "notesSlides"
    if notes.exists():
        shutil.rmtree(notes)
    ct = BUILD / CT
    x = ct.read_text()
    x = re.sub(r'<Override PartName="/ppt/(slides|notesSlides)/[^"]*"[^>]*/>', "", x)
    ct.write_text(x)
    rels = BUILD / "ppt" / "_rels" / "presentation.xml.rels"
    x = rels.read_text()
    x = re.sub(r'<Relationship [^>]*Target="slides/slide\d+\.xml"/>', "", x)
    rels.write_text(x)


def register_slide(n, layout):
    """Create ppt/slides/slideN.xml bound to a layout and register it everywhere."""
    slides = BUILD / "ppt" / "slides"
    (slides / "_rels").mkdir(parents=True, exist_ok=True)
    path = slides / f"slide{n}.xml"
    (slides / "_rels" / f"slide{n}.xml.rels").write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Relationships xmlns="{REL_NS}"><Relationship Id="rId1" Type="{LAYOUT_REL}" Target="../slideLayouts/{layout}"/></Relationships>')
    ct = BUILD / CT
    ct.write_text(ct.read_text().replace("</Types>",
        f'<Override PartName="/ppt/slides/slide{n}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>'))
    rels = BUILD / "ppt" / "_rels" / "presentation.xml.rels"
    rid = f"rIdSlide{n}"
    rels.write_text(rels.read_text().replace("</Relationships>",
        f'<Relationship Id="{rid}" Type="{SLIDE_REL}" Target="slides/slide{n}.xml"/></Relationships>'))
    pres = BUILD / "ppt" / "presentation.xml"
    x = pres.read_text()
    entry = f'<p:sldId id="{255 + n}" r:id="{rid}"/>'
    x = x.replace("<p:sldIdLst/>", f"<p:sldIdLst>{entry}</p:sldIdLst>") if "<p:sldIdLst/>" in x \
        else x.replace("</p:sldIdLst>", f"{entry}</p:sldIdLst>")
    pres.write_text(x)
    return path


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()
    with zipfile.ZipFile(TEMPLATE) as z:
        z.extractall(BUILD)

    # Drop the template's sample slides from the slide list, then add ours from its layouts.
    pres = BUILD / "ppt" / "presentation.xml"
    x = pres.read_text()
    x = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "<p:sldIdLst/>", x, flags=re.S)
    pres.write_text(x)

    remove_template_slides()
    layouts = ["slideLayout1.xml", "slideLayout8.xml", "slideLayout8.xml", "slideLayout8.xml",
               "slideLayout8.xml", "slideLayout8.xml", "slideLayout2.xml"]
    paths = [register_slide(i + 1, lay) for i, lay in enumerate(layouts)]

    builders = [slide_title, lambda: slide_usecase(2), lambda: slide_flow(3), lambda: slide_match(4),
                lambda: slide_never(5), lambda: slide_steps(6), slide_close]
    for n, (p, b) in enumerate(zip(paths, builders), 1):
        _anim.clear()
        p.write_text(slide_xml(b()), encoding="utf-8")
        add_notes(n, NOTES[n])

    # Zip with [Content_Types].xml first.
    if OUT.exists():
        OUT.unlink()
    files = sorted(f for f in BUILD.rglob("*") if f.is_file())
    files.sort(key=lambda f: (f.name != "[Content_Types].xml", str(f)))
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(BUILD).as_posix())
    shutil.rmtree(BUILD)
    print("wrote", OUT, "with", len(paths), "slides")


if __name__ == "__main__":
    main()
