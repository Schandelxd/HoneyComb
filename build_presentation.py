import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_full_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette: Obsidian Dark + Amber Gold + Electric Cyan
    C_BG = RGBColor(12, 14, 20)          # #0c0e14 obsidian dark
    C_CARD = RGBColor(20, 24, 36)        # #141824 elevated card
    C_CARD_HI = RGBColor(28, 34, 52)     # #1c2234 card highlight
    C_BORDER = RGBColor(38, 46, 68)      # #262e44 subtle border
    C_GOLD = RGBColor(245, 158, 11)      # #f59e0b amber gold
    C_GOLD_LT = RGBColor(251, 191, 36)   # #fbbf24 light gold
    C_CYAN = RGBColor(56, 189, 248)      # #38bdf8 electric cyan
    C_GREEN = RGBColor(52, 211, 153)     # #34d399 emerald green
    C_CORAL = RGBColor(248, 113, 113)    # #f87171 soft coral
    C_WHITE = RGBColor(248, 250, 252)    # #f8fafc crisp white
    C_MUTED = RGBColor(148, 163, 184)    # #94a3b8 slate text
    C_MUTED_DK = RGBColor(100, 116, 139) # #64748b dark slate

    FONT_TITLE = "Segoe UI"
    FONT_BODY = "Segoe UI"
    FONT_CODE = "Consolas"

    def setup_slide_chrome(slide, cat_tag, title_text, subtitle_text, slide_num, total_slides=25):
        # 1. Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.color.rgb = C_BG

        # 2. Header Area
        hdr_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.05))
        tf = hdr_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = cat_tag.upper()
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = C_GOLD
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_MUTED

        # Accent Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.color.rgb = C_BORDER

        # 3. Footer Area
        ftr_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.015))
        ftr_line.fill.solid()
        ftr_line.fill.fore_color.rgb = C_BORDER
        ftr_line.line.color.rgb = C_BORDER

        ftr_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(11.733), Inches(0.35))
        ftf = ftr_box.text_frame
        ftf.word_wrap = True
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.font.name = FONT_BODY
        fp.font.size = Pt(9)
        fp.font.color.rgb = C_MUTED_DK

        run_left = fp.add_run()
        run_left.text = "HoneyComb: From-Scratch Text-to-Image Diffusion & Web Studio | KIIT Major Project    "

        run_mid = fp.add_run()
        run_mid.text = f"Slide {slide_num} of {total_slides}    "
        run_mid.font.color.rgb = C_GOLD_LT
        run_mid.font.bold = True

        run_rt = fp.add_run()
        run_rt.text = "School of Computer Engineering, KIIT-DU"

    def add_card(slide, left, top, width, height, bg_color=C_CARD, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    def add_bullet_card(slide, left, top, width, height, title, items, title_color=C_GOLD, bg_color=C_CARD, border_color=C_BORDER):
        add_card(slide, left, top, width, height, bg_color, border_color)
        tbox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.18), width - Inches(0.4), height - Inches(0.36))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(8)

        for heading, body in items:
            p = tf.add_paragraph()
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            p.space_after = Pt(6)

            r_dot = p.add_run()
            r_dot.text = "• "
            r_dot.font.color.rgb = C_GOLD_LT
            r_dot.font.bold = True

            if heading:
                r_h = p.add_run()
                r_h.text = f"{heading}: "
                r_h.font.bold = True
                r_h.font.color.rgb = C_WHITE

            r_b = p.add_run()
            r_b.text = body
            r_b.font.color.rgb = C_MUTED

    def add_metric_card(slide, left, top, width, height, value_str, label_str, subtext="", val_color=C_GOLD_LT):
        add_card(slide, left, top, width, height, C_CARD, C_BORDER)
        tbox = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = value_str
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(28)
        p0.font.bold = True
        p0.font.color.rgb = val_color
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = label_str
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_after = Pt(2)

        if subtext:
            p2 = tf.add_paragraph()
            p2.text = subtext
            p2.font.name = FONT_BODY
            p2.font.size = Pt(9)
            p2.font.color.rgb = C_MUTED

    def add_image_card(slide, left, top, width, height, img_path, caption="", border_color=C_BORDER):
        add_card(slide, left, top, width, height, C_CARD, border_color)
        if os.path.exists(img_path):
            img_top = top + Inches(0.1)
            img_h = height - Inches(0.4) if caption else height - Inches(0.2)
            slide.shapes.add_picture(img_path, left + Inches(0.1), img_top, width - Inches(0.2), img_h)
        else:
            tbox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.4), width - Inches(0.4), height - Inches(0.8))
            tf = tbox.text_frame
            p = tf.paragraphs[0]
            p.text = f"[Image File Not Found: {img_path}]"
            p.font.color.rgb = C_CORAL

        if caption:
            cbox = slide.shapes.add_textbox(left + Inches(0.1), top + height - Inches(0.32), width - Inches(0.2), Inches(0.25))
            ctf = cbox.text_frame
            ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0
            cp = ctf.paragraphs[0]
            cp.text = caption
            cp.font.name = FONT_BODY
            cp.font.size = Pt(8.5)
            cp.font.color.rgb = C_MUTED
            cp.alignment = PP_ALIGN.CENTER

    print("Building 25 presentation slides...")

    # =========================================================================
    # SLIDE 1: Title & Team
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_BG
    bg1.line.color.rgb = C_BG

    tbox1 = s1.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(11.733), Inches(2.2))
    ttf1 = tbox1.text_frame
    ttf1.word_wrap = True
    ttf1.margin_left = ttf1.margin_top = ttf1.margin_right = ttf1.margin_bottom = 0

    p_badge = ttf1.paragraphs[0]
    p_badge.text = "B.TECH CSE MAJOR PROJECT (2023–2027) | KIIT DEEMED TO BE UNIVERSITY"
    p_badge.font.name = FONT_TITLE
    p_badge.font.size = Pt(10)
    p_badge.font.bold = True
    p_badge.font.color.rgb = C_GOLD
    p_badge.space_after = Pt(4)

    p_title = ttf1.add_paragraph()
    p_title.text = "HoneyComb"
    p_title.font.name = FONT_TITLE
    p_title.font.size = Pt(36)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE
    p_title.space_after = Pt(4)

    p_sub = ttf1.add_paragraph()
    p_sub.text = "A 4-Level Text-to-Image Diffusion Model Trained from Scratch with a Real-Time Web Studio"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = C_CYAN
    p_sub.space_after = Pt(4)

    p_desc = ttf1.add_paragraph()
    p_desc.text = "Pixel-Space Denoising Diffusion | Min-SNR Loss | DDIM Fast Sampling | Classifier-Free Guidance | FastAPI Serving"
    p_desc.font.name = FONT_BODY
    p_desc.font.size = Pt(10.5)
    p_desc.font.color.rgb = C_MUTED

    members = [
        ("Souhardya Kar", "Roll: 23052357", "Lead Architecture & Attention Mechanisms", "4-level U-Net topology, cross & self-attention, skip tensor alignment."),
        ("Shubhankar Chandel", "Roll: 2350817", "Inference Engine & Web Studio UI/UX", "DDIM sampler, CFG extrapolation, FastAPI backend, modern dark studio UI."),
        ("Yatharth Jatav", "Roll: 23052207", "Training Pipeline & Min-SNR Loss", "MS-COCO pipeline, Min-SNR-γ loss weighting, EMA tracking, Kaggle checkpoints."),
        ("Uttaran Pal", "Roll: 23053387", "Dataset Preprocessing & Tokenization", "SentenceTransformer embedding, text masking, dataset caching & augmentation."),
        ("Soudas Mukherjee", "Roll: 24057075", "Benchmarking & Experimental Analytics", "CLIP scoring suite, Best-of-N reranking, cross-category metric analysis.")
    ]

    card_w = Inches(2.22)
    card_gap = Inches(0.15)
    start_x = Inches(0.8)

    for i, (name, roll, role, desc) in enumerate(members):
        cx = start_x + i * (card_w + card_gap)
        add_card(s1, cx, Inches(2.95), card_w, Inches(2.75), bg_color=C_CARD, border_color=C_GOLD if i == 0 else C_BORDER)
        cbox = s1.shapes.add_textbox(cx + Inches(0.12), Inches(3.07), card_w - Inches(0.24), Inches(2.51))
        ctf = cbox.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0

        p = ctf.paragraphs[0]
        p.text = name
        p.font.name = FONT_TITLE
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(2)

        p2 = ctf.add_paragraph()
        p2.text = roll
        p2.font.name = FONT_CODE
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_GOLD_LT
        p2.space_after = Pt(4)

        p3 = ctf.add_paragraph()
        p3.text = role
        p3.font.name = FONT_TITLE
        p3.font.size = Pt(8.5)
        p3.font.bold = True
        p3.font.color.rgb = C_CYAN
        p3.space_after = Pt(6)

        p4 = ctf.add_paragraph()
        p4.text = desc
        p4.font.name = FONT_BODY
        p4.font.size = Pt(8.5)
        p4.font.color.rgb = C_MUTED

    add_card(s1, Inches(0.8), Inches(5.85), Inches(11.733), Inches(0.95), bg_color=C_CARD_HI, border_color=C_BORDER)
    infobox = s1.shapes.add_textbox(Inches(1.0), Inches(5.93), Inches(11.333), Inches(0.79))
    itf = infobox.text_frame
    itf.word_wrap = True
    itf.margin_left = itf.margin_top = itf.margin_right = itf.margin_bottom = 0

    ip1 = itf.paragraphs[0]
    ip1.text = "PROJECT SUPERVISION & ACADEMIC AFFILIATION:"
    ip1.font.name = FONT_TITLE
    ip1.font.size = Pt(9)
    ip1.font.bold = True
    ip1.font.color.rgb = C_GOLD

    ip2 = itf.add_paragraph()
    ip2.text = "Under the Guidance of: [Guide Name], [Guide Designation / Department]  |  School of Computer Engineering, KIIT-DU"
    ip2.font.name = FONT_BODY
    ip2.font.size = Pt(10)
    ip2.font.color.rgb = C_WHITE

    ip3 = itf.add_paragraph()
    ip3.text = "Open-Source Implementation: https://github.com/Schandelxd/HoneyComb  (MIT License)"
    ip3.font.name = FONT_CODE
    ip3.font.size = Pt(9)
    ip3.font.color.rgb = C_CYAN

    s1.notes_slide.notes_text_frame.text = (
        "Welcome respected members of the evaluation committee. Today, our team is presenting HoneyComb, an end-to-end "
        "text-to-image diffusion system designed, trained from scratch on MS-COCO, and deployed with a custom real-time Web Studio. "
        "Our project investigates the internal algorithmic mechanics of generative diffusion without relying on commercial closed APIs."
    )

    # =========================================================================
    # SLIDE 2: Problem Statement & Motivation
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s2, "Project Motivation", "The Compute & Abstraction Barrier in Generative AI", "Why building a complete diffusion model from scratch matters for systems research", 2)

    add_bullet_card(s2, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "Industrial Compute Gatekeeping", [
        ("Hyper-Scale Barrier", "Modern diffusion foundation models (SDXL, Imagen, Flux) train on hundreds of H100 GPUs at 512x512 to 1024x1024 resolutions."),
        ("Prohibitive Capital Cost", "Requires hundreds of thousands of dollars in compute, placing foundational research out of reach for academic institutions."),
        ("Resource Disconnect", "Creates a massive divide between industrial AI labs and computer science educational programs.")
    ])

    add_bullet_card(s2, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "The Black-Box API Dilemma", [
        ("Opaque Mechanics", "Commercial image APIs (Midjourney, DALL-E 3) hide loss dynamics, noise schedules, and cross-attention tensor interactions."),
        ("Superficial Integration", "Building wrappers around existing endpoints does not provide deeper understanding of score matching or variance schedules."),
        ("No Architectural Agency", "Researchers cannot probe cross-attention conditioning, guidance extrapolation, or custom layer topologies.")
    ])

    add_bullet_card(s2, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "Our Core Research Mission", [
        ("From-Scratch Engineering", "Architect, train, and serve a complete 91.4M parameter text-to-image pipeline on free commodity GPUs (Kaggle dual T4s)."),
        ("Mathematical Transparency", "Implement exact formulations: cosine variance schedule, Min-SNR-γ loss, DDIM, and Classifier-Free Guidance."),
        ("Interactive Production Studio", "Pair the trained weights with an asynchronous FastAPI engine and modern Web Studio interface.")
    ], border_color=C_GOLD)

    s2.notes_slide.notes_text_frame.text = (
        "In this slide, we motivate why we built HoneyComb from scratch. Generative AI has become dominated by industrial foundation "
        "models that cost hundreds of thousands of dollars to train, while commercial APIs treat generation as an opaque black box. "
        "Our mission was to dismantle this barrier by building every mathematical component ourselves—from raw tensor cross-attention "
        "to deterministic reverse sampling—within accessible academic hardware boundaries."
    )

    # =========================================================================
    # SLIDE 3: Project Objectives
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s3, "Project Scope", "Five Core Engineering & Research Pillars", "Concrete system deliverables executed by the HoneyComb project", 3)

    objs = [
        ("1. Custom 4-Level U-Net", "Design and parameterize a 91.4M parameter U-Net backbone with spatial self-attention, token-level cross-attention, and FiLM conditioning."),
        ("2. End-to-End Training", "Train directly in 128x128x3 pixel space on MS-COCO 2017 using Min-SNR-γ loss weighting, EMA tracking, and Kaggle quota-aware checkpointing."),
        ("3. Fast Inference Engine", "Implement non-Markovian DDIM sampling reducing reverse steps from 1,000 to 20-50, integrated with Classifier-Free Guidance (CFG)."),
        ("4. Real-Time Web Studio", "Develop an asynchronous FastAPI backend and a bespoke obsidian dark UI with seed locking, batch generation, and stage view."),
        ("5. Empirical Benchmarking", "Evaluate quantitative alignment via CLIP ViT-B/32, Best-of-N stochastic reranking, and systematic cross-category ablations.")
    ]

    for i, (title, desc) in enumerate(objs):
        oy = Inches(1.75) + i * Inches(0.98)
        add_card(s3, Inches(0.8), oy, Inches(11.733), Inches(0.85), bg_color=C_CARD, border_color=C_BORDER)
        add_card(s3, Inches(0.95), oy + Inches(0.12), Inches(0.6), Inches(0.6), bg_color=C_CARD_HI, border_color=C_GOLD)

        ibox = s3.shapes.add_textbox(Inches(0.95), oy + Inches(0.15), Inches(0.6), Inches(0.6))
        itf = ibox.text_frame
        ip = itf.paragraphs[0]
        ip.text = str(i + 1)
        ip.font.name = FONT_TITLE
        ip.font.size = Pt(16)
        ip.font.bold = True
        ip.font.color.rgb = C_GOLD_LT
        ip.alignment = PP_ALIGN.CENTER

        tbox = s3.shapes.add_textbox(Inches(1.7), oy + Inches(0.12), Inches(10.6), Inches(0.65))
        ttf = tbox.text_frame
        ttf.word_wrap = True
        ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0

        p = ttf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(2)

        p2 = ttf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_MUTED

    s3.notes_slide.notes_text_frame.text = (
        "These five pillars define the technical scope of HoneyComb. We did not simply train a toy model; we architected a 91.4M "
        "parameter backbone, engineered a fault-tolerant training pipeline that survived Kaggle's 12-hour session limits, implemented "
        "fast non-Markovian sampling, built a production-grade Web Studio, and executed a rigorous CLIP evaluation suite."
    )

    # =========================================================================
    # SLIDE 4: Generative Paradigms: Why Diffusion?
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s4, "Theoretical Foundations", "Generative Paradigms: Why Diffusion?", "Comparative analysis of GANs, VAEs, and Denoising Diffusion Probabilistic Models", 4)

    add_bullet_card(s4, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "Generative Adversarial Networks", [
        ("Minimax Optimization", "Trained via zero-sum game min_G max_D V(D, G), leading to oscillatory training dynamics."),
        ("Mode Collapse", "Generators frequently collapse into generating a limited subset of modes, ignoring data diversity."),
        ("Vanishing Gradients", "Discriminator outpaces generator early in training, stalling gradient feedback."),
        ("Sampling Advantage", "Single forward pass generation, but mathematically brittle and uninvertible.")
    ], title_color=C_CORAL)

    add_bullet_card(s4, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "Variational Autoencoders", [
        ("Likelihood Objective", "Optimizes Evidence Lower Bound (ELBO) via encoder-decoder parameterization."),
        ("Blurry Reconstructions", "Pixel-space L2 loss averages plausible color values across ambiguous boundaries."),
        ("Unimodal Gaussian Prior", "Standard N(0, I) prior fails to capture complex, multi-modal natural image manifolds."),
        ("Inference Speed", "Fast 1-step latent decode, but inherently restricted in high-frequency perceptual fidelity.")
    ], title_color=C_CYAN)

    add_bullet_card(s4, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "Diffusion Models (HoneyComb)", [
        ("Stable Likelihood Proxy", "Formulated as progressive score matching; objective is standard supervised regression on added noise."),
        ("Exceptional Mode Coverage", "Markovian perturbation ensures all modes of the data distribution are stably covered."),
        ("No Adversarial Instability", "Monotonic loss convergence without discriminator collapse or minimax oscillation."),
        ("Granular Test-Time Control", "Steered dynamically during reverse inference via Classifier-Free Guidance (CFG).")
    ], title_color=C_GREEN, border_color=C_GOLD)

    s4.notes_slide.notes_text_frame.text = (
        "Comparing deep generative paradigms reveals why diffusion models have superseded GANs and VAEs. GANs suffer from minimax "
        "instability and mode collapse, while VAEs produce blurry averages due to simple Gaussian priors. Diffusion models convert "
        "complex generation into a sequence of tractable denoising steps, offering stable convergence and full mode coverage."
    )

    # =========================================================================
    # SLIDE 5: Mathematical Foundations: How Diffusion Works
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s5, "Mathematical Modeling", "How Diffusion Works: Perturbation & Denoising", "Forward Markovian perturbation and learned reverse denoising dynamics", 5)

    add_bullet_card(s5, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.9), "Continuous Score Matching Dynamics", [
        ("Forward Perturbation q(x_t|x_0)", "Gradually injects Gaussian noise according to variance schedule β_t. Closed-form jump: x_t = sqrt(α_bar_t) x_0 + sqrt(1 - α_bar_t) ε, where ε ~ N(0, I)."),
        ("Cosine Variance Schedule", "Prevents abrupt destruction of image information early in diffusion, retaining semantic structure longer than linear schedules."),
        ("Reverse Denoising p_θ(x_{t-1}|x_t)", "Neural network parameterizes reverse Gaussian transitions p_θ(x_{t-1}|x_t) = N(x_{t-1}; μ_θ(x_t, t), σ_t^2 I)."),
        ("Noise Predictor ε_θ(x_t, t, c)", "The U-Net does not predict clean pixels directly; it predicts the exact noise vector ε injected into x_t, conditioned on prompt c."),
        ("Analytical Equivalence", "Predicting noise ε is mathematically equivalent to predicting the score of the data distribution ∇_x log p_t(x).")
    ])

    add_image_card(s5, Inches(6.6), Inches(1.75), Inches(5.933), Inches(4.9), "deliverables/fig_diffusion_concept.png", "Figure 5.1: Forward Perturbation q(x_t|x_0) vs Reverse Denoising Dynamics p_θ(x_{t-1}|x_t).")

    s5.notes_slide.notes_text_frame.text = (
        "Here we show the core mathematics of diffusion. In the forward process, Gaussian noise is progressively added to the clean image "
        "using a cosine variance schedule. In the reverse process, our U-Net predicts the injected noise vector epsilon. By parameterizing "
        "noise prediction rather than raw pixels, the model effectively learns the score function of the perturbed data distribution."
    )

    # =========================================================================
    # SLIDE 6: System Overview & Dataflow Pipeline
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s6, "System Architecture", "End-to-End System Overview & Dataflow Pipeline", "From raw textual prompt to conditioned tensor inference and Web Studio serving", 6)

    flow_steps = [
        ("1. Text Conditioning Pipeline", "Prompt Ingestion", "SentenceTransformer ('all-MiniLM-L6-v2') tokenizes text into 24 tokens x 384 dimensions. Applies attention masking and register tokens. 10% unconditional dropout during training for CFG.", C_GOLD),
        ("2. Temporal Modulation (FiLM)", "Timestep Embedding", "Discrete timestep t in [0, 1000] is mapped via sinusoidal positional encodings into 384 dimensions, processed by a 2-layer MLP to generate channel-wise scale (γ) and shift (β) vectors.", C_CYAN),
        ("3. 4-Level U-Net Backbone", "Hierarchical Denoising", "Iterative multi-stage feature extraction across 128->64->32->16 resolutions with skip connections, Squeeze-and-Excitation gating, and multi-head cross-attention.", C_GREEN),
        ("4. Serving & Production Studio", "Real-Time Serving", "FastAPI asynchronous endpoint handles DDIM execution, clamps pixel bounds [-1, 1] to [0, 255] RGB, and delivers base64 PNGs directly to HoneyComb Web Studio.", C_GOLD_LT)
    ]

    for i, (stage, sub, body, color) in enumerate(flow_steps):
        fx = Inches(0.8) + i * Inches(2.98)
        add_card(s6, fx, Inches(1.75), Inches(2.83), Inches(4.9), C_CARD, C_BORDER)

        tbox = s6.shapes.add_textbox(fx + Inches(0.15), Inches(1.9), Inches(2.53), Inches(4.5))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = stage
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = color
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = sub
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_after = Pt(8)

        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_MUTED

    s6.notes_slide.notes_text_frame.text = (
        "This slide presents our system dataflow. The prompt is encoded into a 24 by 384 token matrix by SentenceTransformer. "
        "The diffusion timestep is converted via sinusoidal embeddings into FiLM scales and shifts. Inside the U-Net, cross-attention "
        "binds text semantics to spatial feature maps. Finally, FastAPI serves the generated image to our custom Web Studio."
    )

    # =========================================================================
    # SLIDE 7: HoneyComb 4-Level U-Net Architecture
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s7, "Backbone Topology", "HoneyComb 4-Level U-Net Architecture", "91.4M parameter deep neural network for pixel-space denoising", 7)

    add_bullet_card(s7, Inches(0.8), Inches(1.75), Inches(4.8), Inches(4.9), "Architectural Specifications", [
        ("4 Hierarchical Levels", "Encoder contracts 128x128 -> 64x64 -> 32x32 -> 16x16; decoder mirrors topology with concatenation skip connections."),
        ("Filter Dimensions", "Base filters = 32 with multipliers [1, 2, 4, 8], producing channel depths of [32, 64, 128, 256]. Scalable to 128 base (91.4M params in current weights)."),
        ("Squeeze-and-Excitation (SE)", "Every residual block incorporates SE channel attention with reduction ratio r=16 to adaptively weight feature channels."),
        ("Skip Connections", "Direct feature concatenation across contracting and expanding paths preserves high-frequency spatial boundaries."),
        ("Residual Scaling", "Zero-initialized residual projections ensure stable identity mapping at initialization.")
    ])

    add_image_card(s7, Inches(5.8), Inches(1.75), Inches(6.733), Inches(4.9), "deliverables/fig_arch_diagram.png", "Figure 7.1: HoneyComb 4-Level U-Net Topology with Attention, FiLM, and Skip Connections.")

    s7.notes_slide.notes_text_frame.text = (
        "Here we show the detailed HoneyComb U-Net architecture. It consists of four contracting and four expanding levels, spanning "
        "from 128x128 resolution down to a 16x16 bottleneck. In total, the model encompasses 91.4 million parameters. Each residual "
        "block incorporates Squeeze-and-Excitation gating to recalibrate channel importances dynamically."
    )

    # =========================================================================
    # SLIDE 8: Text Conditioning: Cross-Attention & FiLM
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s8, "Conditioning Mechanisms", "Text Conditioning: Cross-Attention & FiLM", "Token-level multi-head attention and feature-wise linear modulation", 8)

    add_bullet_card(s8, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.9), "Token-Level Multi-Head Cross-Attention", [
        ("Query-Key-Value Formulation", "Spatial feature maps project to Queries Q = W_Q h. Text token embeddings project to Keys K = W_K c and Values V = W_V c."),
        ("Multi-Head Projection", "Attention(Q,K,V) = softmax(Q K^T / sqrt(d_k) + M) V, using 4 heads and text mask M to ignore padding tokens."),
        ("Bottleneck Placement", "Positioned at 32x32 and 16x16 levels where spatial representations align with high-level conceptual semantics."),
        ("Crucial Architectural Fix", "Diagnostic analysis proved spatial self-attention must immediately precede cross-attention at 32x32 encoder and decoder levels to match saved weights."),
        ("Zero-Init Residuals", "Attention output is gated by a zero-initialized scalar gamma before addition to the residual stream.")
    ])

    add_bullet_card(s8, Inches(6.6), Inches(1.75), Inches(5.933), Inches(4.9), "Feature-wise Linear Modulation (FiLM)", [
        ("Affine Feature Modulation", "FiLM modulates normalized spatial activations h using scale γ and shift β: FiLM(h, γ, β) = (1 + γ) ⊙ GroupNorm(h) + β."),
        ("Continuous Timestep Conditioning", "Embeds diffusion time t smoothly into all residual blocks without altering spatial dimensions."),
        ("Lightweight Parameter Footprint", "Computed via compact 2-layer Dense MLP projection from 384-dimensional sinusoidal embeddings."),
        ("Zero-Shift Initialization", "Scale γ and shift β vectors are initialized to zero, allowing identity pass-through at training onset."),
        ("Global Coherence", "Ensures all layers coordinate noise level expectations synchronously across the entire U-Net.")
    ], border_color=C_GOLD)

    s8.notes_slide.notes_text_frame.text = (
        "This slide highlights our two conditioning mechanisms: Cross-Attention and FiLM. Cross-attention allows spatial feature maps "
        "to query text token embeddings directly at the 32x32 and 16x16 resolution levels. A crucial engineering finding during our "
        "weight verification was that spatial self-attention must precede cross-attention at these levels. FiLM applies channel-wise "
        "scale and shift to inform every layer of the current diffusion timestep."
    )

    # =========================================================================
    # SLIDE 9: Training Recipe & Optimization Dynamics
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s9, "Training Methodology", "Training Recipe: Min-SNR Loss & EMA", "Advanced loss formulation, weight averaging, and optimization dynamics", 9)

    add_bullet_card(s9, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "Min-SNR-γ Loss Weighting", [
        ("Variance Collapse in MSE", "Standard diffusion MSE loss treats all timesteps equally, causing optimization collapse at high noise where SNR is near zero."),
        ("Clamped Loss Formulation", "Min-SNR clamps loss weight at γ = 5.0: L = min(SNR(t), γ) ||ε - ε_θ||^2."),
        ("Balanced Gradients", "Prevents high-noise timesteps from dominating gradient norms, dramatically stabilizing multi-head cross-attention convergence.")
    ], title_color=C_GOLD)

    add_bullet_card(s9, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "Exponential Moving Average (EMA)", [
        ("Shadow Weight Tracking", "Maintains moving average of trainable weights: θ_EMA = β θ_EMA + (1 - β) θ with decay β = 0.9999."),
        ("Stochastic Jitter Elimination", "Smooths out noisy parameter fluctuations caused by mini-batch stochastic gradient descent."),
        ("Superior Visual Fidelity", "EMA weights consistently produce sharper edges and fewer high-frequency color artifacts during inference.")
    ], title_color=C_CYAN)

    add_bullet_card(s9, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "Optimization & Regularization", [
        ("AdamW Optimizer", "Learning rate 1e-4 with weight decay 1e-4 to regularize dense projection kernels."),
        ("Gradient Clipping", "Global norm clipped strictly at 1.0 to prevent exploding gradient bursts through cross-attention."),
        ("Unconditional Text Dropout", "10% of prompts replaced with empty token string during training to enable Classifier-Free Guidance at test time.")
    ], title_color=C_GREEN)

    s9.notes_slide.notes_text_frame.text = (
        "Our training recipe incorporates three vital techniques. First, Min-SNR loss weighting clamps the signal-to-noise ratio at "
        "gamma equals 5.0, preventing noisy timesteps from overwhelming gradient descent. Second, Exponential Moving Average with "
        "beta of 0.9999 tracks smooth shadow weights for inference. Third, 10% unconditional text dropout trains the model to generate "
        "both conditioned and unconditioned estimates for Classifier-Free Guidance."
    )

    # =========================================================================
    # SLIDE 10: Kaggle Quota-Aware Training Infrastructure
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s10, "Systems Engineering", "Kaggle Quota-Aware Training Infrastructure", "Surviving strict 12-hour cloud GPU execution limits without data loss", 10)

    add_bullet_card(s10, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "The 12-Hour Quota Challenge", [
        ("Hard Execution Boundaries", "Free cloud GPU tiers (Kaggle dual T4/P100) enforce an unnegotiable 12-hour session termination ceiling."),
        ("Silent Preemption Risk", "Sessions terminate abruptly; writes in progress during shutdown result in truncated, unrecoverable weight files."),
        ("Multi-Day Convergence", "Training HoneyComb across 86,660 steps required over 45 GPU hours, spanning 5 discrete sessions.")
    ], title_color=C_CORAL)

    add_bullet_card(s10, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "Dual-Slot Ping-Pong Checkpointing", [
        ("Alternating Slot Writes", "Checkpoints alternate strictly between weights_slotA.h5 and weights_slotB.h5."),
        ("Atomic Safety Guarantee", "If a session aborts while writing Slot A, Slot B remains 100% valid and loadable, preventing catastrophic loss."),
        ("Verification Checksum", "Each write validates HDF5 header integrity before registering the active slot pointer.")
    ], title_color=C_CYAN)

    add_bullet_card(s10, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "Comprehensive State Tracking", [
        ("Metadata Persistence", "State file train_state.json records exact epoch, global step, AdamW momentum buffers, and PRNG seeds."),
        ("Automated Resume Script", "Startup harness inspects metadata, identifies the latest intact slot, and resumes training within 15 seconds."),
        ("Zero Waste Engineering", "Zero duplicate compute cycles across disconnected Kaggle sessions.")
    ], title_color=C_GREEN, border_color=C_GOLD)

    s10.notes_slide.notes_text_frame.text = (
        "Training a 91.4M parameter model on free cloud resources required robust systems engineering. Kaggle enforces a strict 12-hour "
        "session limit. To prevent data corruption during mid-write session cutoffs, we engineered a dual-slot ping-pong checkpointing "
        "system. An accompanying train_state.json metadata file preserved optimizer momentum and step counts, allowing instantaneous "
        "warm-restarts across disconnected sessions."
    )

    # =========================================================================
    # SLIDE 11: Training Progression: Visual Convergence
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s11, "Empirical Convergence", "Training Progression: Visual Quality Evolution", "Step-by-step visual convergence on MS-COCO 2017 across 86,660 gradient steps", 11)

    add_bullet_card(s11, Inches(0.8), Inches(1.75), Inches(4.6), Inches(4.9), "Empirical Training Milestones", [
        ("Step 1,780: Pure Noise", "Zero spatial structure; model generates uniform Gaussian noise without color partitioning."),
        ("Step 8,900: Global Chrominance", "Emergence of global color fields and coarse foreground-background horizon lines."),
        ("Step 26,700: Object Geometry", "Distinct object contours, animal silhouettes, and vehicle boundaries become visible."),
        ("Step 53,400: Semantic Grounding", "Coherent subjects with recognizable features (dog ears, vehicle wheels) and contextual shadows."),
        ("Step 86,660: Converged Synthesis", "Fine surface textures (grass blades, fur, reflections), balanced contrast, and robust prompt adherence.")
    ])

    add_image_card(s11, Inches(5.6), Inches(1.75), Inches(6.933), Inches(4.9), "deliverables/fig_training_progression.png", "Figure 11.1: Visual Convergence Progression across Steps 1,780, 8,900, 17,800, 35,600, 53,400, and 86,660.")

    s11.notes_slide.notes_text_frame.text = (
        "Figure 11.1 illustrates the empirical visual progression across 86,660 training steps on MS-COCO. Early steps show pure noise, "
        "followed by macro-level color field separation by step 8,900. By step 26,700, geometric contours crystallize. By step 86,660, "
        "the model synthesizes sharp, photometrically coherent subjects with realistic background textures."
    )

    # =========================================================================
    # SLIDE 12: Inference Engine: DDIM Fast Sampling & CFG
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s12, "Fast Inference", "Inference Engine: DDIM Fast Sampling & CFG", "Accelerating reverse diffusion by 20x with Classifier-Free Guidance extrapolation", 12)

    add_bullet_card(s12, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.9), "DDIM Non-Markovian Acceleration", [
        ("Deterministic Sampling Path", "Formulates an implicit non-Markovian forward process sharing exact marginal distributions with DDPM."),
        ("Step Compression: 1000 -> 20-50", "Allows skipping hundreds of intermediate timesteps, cutting inference latency from 45 seconds down to 1.8 seconds (20x speedup)."),
        ("Zero Stochastic Drift", "With η = 0.0, the sampling trajectory becomes purely deterministic given an initial Gaussian noise seed x_T."),
        ("Reversible Latent Inversion", "Deterministic trajectories allow consistent latent encoding and editing.")
    ], title_color=C_CYAN)

    add_bullet_card(s12, Inches(6.6), Inches(1.75), Inches(5.933), Inches(4.9), "Classifier-Free Guidance (CFG)", [
        ("Score Extrapolation Formula", "ε_hat = ε_θ(x_t, ∅) + w · (ε_θ(x_t, c) - ε_θ(x_t, ∅)), where w is the guidance scale."),
        ("Negative Score Steering", "Pushes the generative trajectory away from generic unconditional modes toward the conditioning prompt subspace."),
        ("Contrast & Sharpness Amplification", "Significantly sharpens subject outlines and enhances color saturation at w = 5.0 - 7.5."),
        ("No Auxiliary Classifier", "Eliminates the need for a separate noisy classifier network (as in Ho & Salimans).")
    ], title_color=C_GOLD, border_color=C_GOLD)

    s12.notes_slide.notes_text_frame.text = (
        "Inference efficiency is governed by two algorithmic breakthroughs: DDIM and Classifier-Free Guidance. Standard DDPM requires "
        "1,000 sequential steps, which takes nearly a minute per image. DDIM formulates a non-Markovian deterministic trajectory, reducing "
        "steps to between 20 and 50 with virtually zero perceptual penalty. Classifier-Free Guidance extrapolates predicted noise away from "
        "the unconditioned estimate, greatly amplifying prompt adherence."
    )

    # =========================================================================
    # SLIDE 13: HoneyComb Web Studio Interface
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s13, "Production Deployment", "HoneyComb Web Studio Interface", "Production-grade dark studio UI paired with real-time FastAPI asynchronous backend", 13)

    add_image_card(s13, Inches(0.8), Inches(1.75), Inches(6.2), Inches(4.9), "deliverables/ui_screenshot.png", "Figure 13.1: HoneyComb Web Studio Production Interface Screenshot (Obsidian Dark Theme).")

    add_bullet_card(s13, Inches(7.2), Inches(1.75), Inches(5.333), Inches(4.9), "Web Studio Engineering Highlights", [
        ("Obsidian Dark Design System", "Custom dark UI (#09090c) with amber-gold accents, Inter typography, and responsive CSS grid layout."),
        ("Deterministic Seed Locking", "Toggleable seed lock using tf.random.set_seed ensures 100% reproducible prompt experimentation."),
        ("Batch Generation (1, 2, 4)", "Supports concurrent multi-image synthesis with responsive canvas grid display."),
        ("Curated Preset Categorization", "Integrated tabs for Everyday, Animals, Food, Outdoors, and Indoors prompt benchmarks."),
        ("Stage Inspection & Export", "Fullscreen modal stage view for detail inspection and 512px upscaled PNG download."),
        ("Client-Side History State", "Persists previous generations and prompt settings locally using HTML5 localStorage.")
    ], border_color=C_GOLD)

    s13.notes_slide.notes_text_frame.text = (
        "Figure 13.1 shows our production Web Studio interface, accessible at localhost:8000. It features a bespoke dark theme with "
        "amber-gold accents, built using modern vanilla HTML5, CSS, and JS. It offers deterministic seed locking for reproducibility, "
        "multi-image batch generation, curated category presets, a fullscreen stage inspection mode, and client-side history persistence."
    )

    # =========================================================================
    # SLIDE 14: Quantitative Evaluation Methodology
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s14, "Experimental Rigor", "Quantitative Evaluation Methodology", "CLIP ViT-B/32 text-image alignment scoring and Best-of-N stochastic reranking", 14)

    add_bullet_card(s14, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "CLIP Alignment Scoring", [
        ("OpenAI ViT-B/32 Space", "Leverages pretrained openai/clip-vit-base-patch32 multimodal embedding model."),
        ("Cosine Similarity Metric", "CLIP = 100 × (v_img · v_txt) / (||v_img|| ||v_txt||)."),
        ("Objective Assessment", "Provides reproducible numeric validation of text-image alignment free from human evaluation bias.")
    ], title_color=C_CYAN)

    add_bullet_card(s14, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "Best-of-N Stochastic Reranking", [
        ("Test-Time Compute Search", "Generates N independent diffusion trajectories using varying random seeds for the same prompt."),
        ("Automated Ranking", "CLIP scores every generated sample and selects the candidate maximizing semantic alignment."),
        ("Quality Amplification", "Extracts optimal samples without modifying or retraining model weights.")
    ], title_color=C_GOLD)

    add_bullet_card(s14, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "29-Prompt Evaluation Suite", [
        ("5 Semantic Domains", "Evaluated across Rigid Scenes (8), Animals (7), People & Sports (5), Outdoors (5), and Out-of-Domain (4)."),
        ("MS-COCO Style Prompts", "Standard photographic prompts matching training distribution, plus challenging out-of-domain concepts."),
        ("Comprehensive Metrics", "Tracks Best, Mean, and Worst CLIP scores across all seeds.")
    ], title_color=C_GREEN)

    s14.notes_slide.notes_text_frame.text = (
        "To evaluate HoneyComb quantitatively without subjective bias, we utilized OpenAI's CLIP ViT-B/32 model to compute text-image "
        "cosine similarity. We also implemented Best-of-N stochastic reranking, where multiple diffusion trajectories are sampled with "
        "different seeds and reranked using CLIP. Our benchmark encompasses 29 standardized prompts across five semantic categories."
    )

    # =========================================================================
    # SLIDE 15: Empirical Sweeps: Guidance Scale & Denoising Steps
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s15, "Parameter Ablation", "Parameter Sweeps: Guidance Scale & Steps", "Empirical sensitivity analysis across Classifier-Free Guidance scales and DDIM step counts", 15)

    add_image_card(s15, Inches(0.8), Inches(1.75), Inches(4.6), Inches(4.9), "fig_guidance.png", "Figure 15.1: CFG Guidance Scale Sweep (1.0, 3.0, 5.0, 7.5, 10.0).")
    add_image_card(s15, Inches(5.6), Inches(1.75), Inches(3.8), Inches(4.9), "fig_steps.png", "Figure 15.2: DDIM Step Sweep (10, 20, 30, 50 Steps).")

    add_bullet_card(s15, Inches(9.6), Inches(1.75), Inches(2.933), Inches(4.9), "Empirical Insights", [
        ("Guidance Sweet Spot", "Scale w in [5.0, 7.5] yields maximum fidelity. Scale 1.0 is washed out; scale 10.0 causes saturation clipping."),
        ("Step Convergence", "Visual structure stabilizes by step 20-30. 50 steps provides minimal gain (+0.3 CLIP) for 2x latency."),
        ("Optimal Operating Point", "Configuring w=5.0 and S=30 offers the optimal Pareto balance for real-time serving.")
    ], title_color=C_GOLD, border_color=C_GOLD)

    s15.notes_slide.notes_text_frame.text = (
        "This slide presents empirical sweeps across guidance scale and step count. In Figure 15.1, we see guidance scale 1.0 produces "
        "low contrast, while scale 10.0 causes unnatural oversaturation; the sweet spot lies at 5.0 to 7.5. In Figure 15.2, step count "
        "sweep shows rapid convergence by 20 to 30 steps, proving that 30 steps is the optimal operating point for interactive serving."
    )

    # =========================================================================
    # SLIDE 16: Quantitative Results: CFG & Best-of-N Impact
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s16, "Empirical Benchmark", "Quantitative Performance: CFG & Best-of-N Gains", "Real measurement data from results.csv demonstrating substantial fidelity gains", 16)

    # Metric callout cards
    add_metric_card(s16, Inches(0.8), Inches(1.75), Inches(3.7), Inches(1.5), "+17.3%", "Classifier-Free Guidance Gain", "Single-image CLIP: 22.85 -> 26.80 at scale 5.0", C_GOLD_LT)
    add_metric_card(s16, Inches(4.8), Inches(1.75), Inches(3.7), Inches(1.5), "+2.20 pts", "Best-of-N Stochastic Boost", "Best-of-4 CLIP reaches 29.00 vs 26.80 single", C_CYAN)
    add_metric_card(s16, Inches(8.8), Inches(1.75), Inches(3.7), Inches(1.5), "+26.9%", "Total System Performance Leap", "Baseline single (22.85) to Best-of-4 CFG (29.00)", C_GREEN)

    # Detailed Table Card
    add_card(s16, Inches(0.8), Inches(3.45), Inches(11.733), Inches(3.2), C_CARD, C_BORDER)
    tbox = s16.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(11.333), Inches(2.9))
    tf = tbox.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_tbl = tf.paragraphs[0]
    p_tbl.text = "EMPIRICAL BENCHMARK SUMMARY (Measured Directly in results.csv)"
    p_tbl.font.name = FONT_TITLE
    p_tbl.font.size = Pt(12)
    p_tbl.font.bold = True
    p_tbl.font.color.rgb = C_GOLD
    p_tbl.space_after = Pt(8)

    rows = [
        ("CFG Off (Scale 1.0)", "22.85", "21.55", "24.68", "Baseline unguided score"),
        ("CFG On (Scale 5.0)", "26.80 (+17.3%)", "26.16 (+21.4%)", "29.00 (+17.5%)", "Substantial guidance alignment boost"),
        ("Net Best-of-N Gain", "+1.83 pts", "—", "+2.20 pts", "Free test-time compute quality gain")
    ]

    p_hdr = tf.add_paragraph()
    p_hdr.text = f"{'Configuration':<25}{'Single Image':<20}{'Mean of 4':<20}{'Best of 4':<20}{'Analysis'}"
    p_hdr.font.name = FONT_CODE
    p_hdr.font.size = Pt(10)
    p_hdr.font.bold = True
    p_hdr.font.color.rgb = C_CYAN
    p_hdr.space_after = Pt(6)

    for cfg, sgl, mn, bst, comm in rows:
        p = tf.add_paragraph()
        p.text = f"{cfg:<25}{sgl:<20}{mn:<20}{bst:<20}{comm}"
        p.font.name = FONT_CODE
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(4)

    p_note = tf.add_paragraph()
    p_note.text = "\nKey Takeaway: CFG provides the single largest semantic alignment boost (+17.3%), while Best-of-N stochastic reranking adds an additional +2.20 CLIP points at test time without model retraining."
    p_note.font.name = FONT_BODY
    p_note.font.size = Pt(10)
    p_note.font.color.rgb = C_MUTED

    s16.notes_slide.notes_text_frame.text = (
        "These numbers are quoted directly from results.csv. Enabling Classifier-Free Guidance at scale 5.0 increases the single-image "
        "CLIP score from 22.85 to 26.80, a 17.3% boost. Best-of-4 reranking further improves the score to 29.00, yielding a cumulative "
        "26.9% increase over the baseline. The average spread between the best and worst seed for a prompt is 4.2 CLIP points."
    )

    # =========================================================================
    # SLIDE 17: Stochastic Quality Distribution: Best vs Worst
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s17, "Seed Sensitivity", "Stochastic Quality Distribution: Best vs Worst", "Analyzing seed variance on prompt: 'a brown dog sitting on the grass'", 17)

    add_image_card(s17, Inches(0.8), Inches(1.75), Inches(5.8), Inches(4.9), "fig_range.png", "Figure 17.1: Visual Quality Range: Best (29.00), Typical (26.80), and Worst (24.80) Realizations.")

    add_bullet_card(s17, Inches(6.8), Inches(1.75), Inches(5.733), Inches(4.9), "Seed Stochasticity & Trajectory Analysis", [
        ("Best Candidate (CLIP 29.00)", "Crisp canine anatomy, centered composition, high-contrast fur texture against green grass, and natural posture."),
        ("Typical Candidate (CLIP 26.80)", "Recognizable dog silhouette and plausible lawn background; slightly softer fur boundaries and moderate figure-ground contrast."),
        ("Worst Candidate (CLIP 24.80)", "Amorphous brown shape, ambiguous limb boundaries, and noisy grass background; lacks distinct facial features."),
        ("Seed Variance Dynamics", "Diffusion is inherently stochastic. Even with high guidance, initial noise seeds determine whether the trajectory lands in a sharp or blurred basin."),
        ("Value of Best-of-N", "Proves that generating 4 samples and selecting the top CLIP candidate effectively eliminates low-quality seed outliers.")
    ], border_color=C_GOLD)

    s17.notes_slide.notes_text_frame.text = (
        "Figure 17.1 demonstrates the impact of random seed stochasticity. For the exact same prompt and guidance settings, the best "
        "sample achieved a CLIP score of 29.00 with clean canine features, while the worst scored 24.80 with ambiguous contours. "
        "This 4.2 point gap proves why Best-of-N reranking is such a high-leverage inference strategy."
    )

    # =========================================================================
    # SLIDE 18: Cross-Category Benchmark Performance
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s18, "Category Analysis", "Benchmark Performance Across Semantic Categories", "Quantitative ranking across 5 distinct prompt domains from group_summary.csv", 18)

    add_image_card(s18, Inches(0.8), Inches(1.75), Inches(5.8), Inches(4.9), "report_out/fig_ranking_all.png", "Figure 18.1: Comprehensive Benchmark Ranking Across Evaluated Benchmark Prompts.")

    add_bullet_card(s18, Inches(6.8), Inches(1.75), Inches(5.733), Inches(4.9), "Category Breakdown (group_summary.csv)", [
        ("Animals (Top Group, Avg Best 33.29)", "Highest performance across all categories. 'A herd of sheep grazing on a hill' achieved the global top score of 33.95."),
        ("Rigid Scenes / Vehicles (Avg Best 30.30)", "Trains, buses, and airplanes exhibit high contrast and rigid geometry that align cleanly with convolutional inductive biases."),
        ("People & Sports (Avg Best 30.11)", "Strong global posture and sports equipment alignment, though fine facial features blur at 128x128 resolution."),
        ("Out of Domain (Avg Best 26.28)", "Concepts absent from COCO (e.g. futuristic cyberpunk cities) suffer semantic hallucination."),
        ("Outdoor Landscapes (Avg Best 26.14)", "Diffuse landscapes (snowy mountains) suffer lower CLIP scores due to broad, texture-heavy compositions.")
    ], border_color=C_CYAN)

    s18.notes_slide.notes_text_frame.text = (
        "Figure 18.1 shows ranked performance across conceptual categories from group_summary.csv. Animals led all categories with an "
        "average best CLIP score of 33.29, with 'a herd of sheep' reaching 33.95. Rigid scenes like vehicles also performed strongly at "
        "30.30. In contrast, out-of-domain prompts and broad landscapes received lower scores due to dataset bias and texture diffusion."
    )

    # =========================================================================
    # SLIDE 19: Qualitative Analysis: What Works vs What Fails
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s19, "Qualitative Audit", "Qualitative Audit: Strengths vs Failure Modes", "Honest assessment of synthesized features, compositional limits, and boundary cases", 19)

    add_bullet_card(s19, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.9), "What Works Exceptionally Well", [
        ("Global Macro Composition", "Plausible scene layout with correct spatial partitioning between sky, terrain, and foreground objects."),
        ("Iconic Object Geometry", "Well-defined silhouettes for common MS-COCO classes (dogs, sheep, trains, buses, pizzas)."),
        ("Organic Texture Rendering", "Convincing rendering of natural textures including grass fields, cloud formations, water, and animal fur."),
        ("Lighting & Contrast", "Classifier-Free Guidance generates vibrant contrast and realistic directional illumination.")
    ], title_color=C_GREEN, border_color=C_GREEN)

    add_bullet_card(s19, Inches(6.6), Inches(1.75), Inches(5.933), Inches(4.9), "Failure Modes & Edge Cases", [
        ("Fine Micro-Anatomy", "Human faces lack eyes and mouth definition; fingers and paws frequently blend into amorphous blobs."),
        ("Legible Text & Typography", "Model cannot render readable alphanumeric characters; generates pseudo-script artifacts."),
        ("Spatial Relational Semantics", "Struggles with relational prepositions (e.g., 'a cat sitting inside a cardboard box')."),
        ("Numeracy & Counting", "Prompts specifying quantities (e.g., 'three apples') frequently yield ambiguous, merged clusters.")
    ], title_color=C_CORAL, border_color=C_CORAL)

    s19.notes_slide.notes_text_frame.text = (
        "A rigorous academic report requires honest qualitative evaluation. HoneyComb excels at macro-composition, iconic object geometry, "
        "organic textures, and scene lighting. However, it struggles with micro-anatomy like human eyes and fingers, cannot render legible "
        "text, and fails at spatial numeracy and relational prepositions like 'under' or 'inside'."
    )

    # =========================================================================
    # SLIDE 20: Fundamental Technical Limitations
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s20, "Boundary Analysis", "Fundamental Technical Limitations", "Core architectural and data boundaries constraining the HoneyComb prototype", 20)

    limits = [
        ("1. Pixel-Space Resolution (128x128x3)", "Direct RGB pixel diffusion scales quadratically with spatial dimensions. Operating directly at 128x128 prohibits fine-grained high-frequency details."),
        ("2. Text Encoder Capacity (24 Tokens)", "The 24-token context window of SentenceTransformer restricts prompt length, truncating complex, multi-clause narrative descriptions."),
        ("3. COCO Dataset Distribution Bias", "MS-COCO 2017 is dominated by photographic everyday objects, causing severe degradation when prompted for abstract, surreal, or stylized concepts."),
        ("4. Non-Markovian Truncation Bounds", "Sub-sampling DDIM below 15 steps introduces noticeable high-frequency noise and muddy colors, limiting extreme real-time acceleration.")
    ]

    for i, (title, body) in enumerate(limits):
        ly = Inches(1.75) + i * Inches(1.22)
        add_card(s20, Inches(0.8), ly, Inches(11.733), Inches(1.08), C_CARD, C_BORDER)
        tbox = s20.shapes.add_textbox(Inches(1.0), ly + Inches(0.12), Inches(11.333), Inches(0.84))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(12)
        p0.font.bold = True
        p0.font.color.rgb = C_CORAL
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = body
        p1.font.name = FONT_BODY
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = C_MUTED

    s20.notes_slide.notes_text_frame.text = (
        "We identify four fundamental limitations in HoneyComb: first, 128x128 pixel resolution bounds high-frequency details; second, "
        "the 24-token text embedding capacity limits prompt expressiveness; third, MS-COCO dataset bias restricts abstract out-of-domain "
        "generalization; fourth, aggressive step subsampling below 15 steps leads to noticeable image degradation."
    )

    # =========================================================================
    # SLIDE 21: Future Research & Roadmap
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s21, "Future Directions", "Future Research Roadmap & Architectural Extensions", "Strategic evolution paths from academic prototype to modern production diffusion", 21)

    futures = [
        ("1. Latent Diffusion Architecture (LDM)", "Train a VQ-VAE or KL-regularized autoencoder with downsampling factor f=4 or f=8. Operating in a 32x32 latent space will allow 512x512 synthesis at reduced compute."),
        ("2. Cascaded Super-Resolution", "Implement a secondary conditional diffusion upsampling model (128x128 -> 512x512) following Ho et al., enabling sharp high-resolution outputs."),
        ("3. Scaled Multimodal Conditioning", "Replace SentenceTransformer with frozen OpenCLIP ViT-H/14 or T5-XXL encoders to enable rich compositional prompt adherence and spatial numeracy."),
        ("4. Consistency Distillation / Flow Matching", "Apply progressive consistency distillation or rectified flow matching to compress sampling down to 1-2 steps for sub-100ms real-time generation.")
    ]

    for i, (title, body) in enumerate(futures):
        fy = Inches(1.75) + i * Inches(1.22)
        add_card(s21, Inches(0.8), fy, Inches(11.733), Inches(1.08), C_CARD, C_BORDER)
        tbox = s21.shapes.add_textbox(Inches(1.0), fy + Inches(0.12), Inches(11.333), Inches(0.84))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(12)
        p0.font.bold = True
        p0.font.color.rgb = C_CYAN
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = body
        p1.font.name = FONT_BODY
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = C_MUTED

    s21.notes_slide.notes_text_frame.text = (
        "Our future roadmap charts four clear upgrade paths: migrating to Latent Diffusion using a VQ-VAE to achieve 512x512 resolution; "
        "training a cascaded super-resolution upsampler; incorporating larger text encoders like OpenCLIP or T5-XXL; and adopting "
        "consistency distillation to achieve single-step sub-100ms real-time generation."
    )

    # =========================================================================
    # SLIDE 22: Team Roles & Contribution Matrix
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s22, "Team Recognition", "Team Roles & Contribution Distribution", "Core module ownership, systems responsibilities, and project management", 22)

    team_roles = [
        ("Souhardya Kar", "Roll: 23052357", "Lead Architecture & Attention Mechanisms", "Designed 4-level U-Net topology, cross-attention projections, self-attention layer placement, skip tensor matching.", "[% Placeholder]"),
        ("Shubhankar Chandel", "Roll: 2350817", "Inference Engine & Web Studio UI/UX", "Implemented fast DDIM sampler, CFG scaling, FastAPI asynchronous backend, and modern dark studio UI.", "[% Placeholder]"),
        ("Yatharth Jatav", "Roll: 23052207", "Training Pipeline & Min-SNR Loss", "Engineered MS-COCO data pipeline, Min-SNR-γ loss formulation, EMA tracking, and Kaggle dual-slot checkpointing.", "[% Placeholder]"),
        ("Uttaran Pal", "Roll: 23053387", "Dataset Preprocessing & Tokenization", "Managed SentenceTransformer tokenization, attention masking, data caching, and augmentation pipelines.", "[% Placeholder]"),
        ("Soudas Mukherjee", "Roll: 24057075", "Benchmarking & Experimental Analytics", "Built CLIP evaluation suite, Best-of-N reranking harness, category ablation benchmarks, and statistical analysis.", "[% Placeholder]")
    ]

    for i, (name, roll, role, contrib, pct) in enumerate(team_roles):
        ty = Inches(1.75) + i * Inches(0.92)
        add_card(s22, Inches(0.8), ty, Inches(11.733), Inches(0.82), C_CARD, C_BORDER)
        tbox = s22.shapes.add_textbox(Inches(1.0), ty + Inches(0.1), Inches(11.333), Inches(0.62))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{i+1}. {name} "
        r1.font.name = FONT_TITLE
        r1.font.size = Pt(11.5)
        r1.font.bold = True
        r1.font.color.rgb = C_WHITE

        r2 = p.add_run()
        r2.text = f"({roll})  —  "
        r2.font.name = FONT_CODE
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = C_GOLD_LT

        r3 = p.add_run()
        r3.text = f"{role}  |  Contr: {pct}"
        r3.font.name = FONT_TITLE
        r3.font.size = Pt(10)
        r3.font.bold = True
        r3.font.color.rgb = C_CYAN
        p.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = contrib
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9)
        p2.font.color.rgb = C_MUTED

    add_card(s22, Inches(0.8), Inches(6.45), Inches(11.733), Inches(0.4), C_CARD_HI, C_BORDER)
    gbox = s22.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.333), Inches(0.3))
    gtf = gbox.text_frame
    gp = gtf.paragraphs[0]
    gp.text = "Project Supervisor: [Guide Name], [Guide Designation / Department]  |  School of Computer Engineering, KIIT-DU"
    gp.font.name = FONT_BODY
    gp.font.size = Pt(9)
    gp.font.color.rgb = C_GOLD_LT

    s22.notes_slide.notes_text_frame.text = (
        "Here we acknowledge the contributions of our five team members. Souhardya led the U-Net architecture and attention layer "
        "alignment; Shubhankar engineered the inference engine and Web Studio; Yatharth directed the training pipeline and Min-SNR "
        "loss implementation; Uttaran managed tokenization and dataset caching; and Soudas directed CLIP benchmarking and statistical "
        "evaluation. We also gratefully acknowledge our guide's supervision."
    )

    # =========================================================================
    # SLIDE 23: Conclusion & Key Learnings
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s23, "Summary & Contributions", "Conclusions & Pedagogical Takeaways", "Summary of project milestones, empirical verifications, and educational impact", 23)

    add_bullet_card(s23, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "Ground-Up Mastery", [
        ("Complete From-Scratch System", "Built an entire generative diffusion ecosystem from raw mathematical foundations without external high-level APIs."),
        ("Architectural Precision", "Resolved complex layer alignment between self-attention and cross-attention tensors."),
        ("Commodity GPU Feasibility", "Proved that a 91.4M parameter diffusion model can be trained successfully on free cloud resources.")
    ], title_color=C_GOLD)

    add_bullet_card(s23, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "Validated Empirical Gains", [
        ("Classifier-Free Guidance", "Quantified a +17.3% CLIP improvement from CFG extrapolation at scale 5.0."),
        ("Best-of-N Reranking", "Demonstrated an additional +2.20 point boost via stochastic reranking at test time."),
        ("Parameter Sweeps", "Mapped exact Pareto-optimal configurations (w=5.0, steps=30) for interactive deployment.")
    ], title_color=C_CYAN)

    add_bullet_card(s23, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "Production Artifacts", [
        ("HoneyComb Web Studio", "Delivered a responsive, dark studio interface with seed locking, batch generation, and stage view."),
        ("FastAPI Serving Backend", "Achieved sub-2 second asynchronous batch generation on local GPU hardware."),
        ("Open-Source Contribution", "Full codebase open-sourced under MIT license on GitHub for educational reproducibility.")
    ], title_color=C_GREEN, border_color=C_GOLD)

    s23.notes_slide.notes_text_frame.text = (
        "In conclusion, HoneyComb successfully demonstrates that an end-to-end text-to-image diffusion pipeline can be architected, "
        "trained from scratch, and served efficiently on accessible hardware. We quantified the immense value of Classifier-Free "
        "Guidance and Best-of-N reranking, delivered a production-ready Web Studio, and open-sourced the entire project under the MIT license."
    )

    # =========================================================================
    # SLIDE 24: Viva Defense: Anticipated Questions & Answers
    # =========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s24, "Viva Defense Preparation", "Viva Defense: Key Technical Inquiries & Answers", "Anticipated examiner questions and rigorous technical explanations", 24)

    vivas = [
        ("Q1: Why train in pixel space instead of latent space?", "Pixel space eliminates autoencoder reconstruction artifacts and compound error propagation. It provides complete mathematical transparency to study attention layer dynamics directly, without reliance on a separate VAE prior."),
        ("Q2: What is the exact mathematical role of Classifier-Free Guidance?", "CFG extrapolates predicted noise away from unconditional prior: ε_hat = ε_u + w(ε_c - ε_u). It acts as a gradient ascent step along the text-conditional score function, sharpening alignment at the cost of diversity."),
        ("Q3: Why is Min-SNR-γ loss superior to standard MSE?", "Standard MSE assigns uniform loss weights across all timesteps. At high noise levels, the tiny signal-to-noise ratio causes massive gradient variance. Clamping at γ = 5.0 stabilizes training and prevents high-noise collapse."),
        ("Q4: How does DDIM achieve 20x faster inference than DDPM?", "DDIM defines a non-Markovian forward process that yields identical marginal distributions q(x_t|x_0). Because the trajectory is deterministic (η=0), the model can skip hundreds of intermediate timesteps safely.")
    ]

    for i, (q, a) in enumerate(vivas):
        vy = Inches(1.75) + i * Inches(1.22)
        add_card(s24, Inches(0.8), vy, Inches(11.733), Inches(1.08), C_CARD, C_BORDER)
        tbox = s24.shapes.add_textbox(Inches(1.0), vy + Inches(0.12), Inches(11.333), Inches(0.84))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = q
        p0.font.name = FONT_TITLE
        p0.font.size = Pt(11.5)
        p0.font.bold = True
        p0.font.color.rgb = C_GOLD_LT
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = a
        p1.font.name = FONT_BODY
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = C_WHITE

    s24.notes_slide.notes_text_frame.text = (
        "This slide prepares the team for common viva questions. The examiners frequently ask why we chose pixel space over latent "
        "space, how CFG operates mathematically, why Min-SNR loss is essential, and how DDIM accelerates sampling. The answers provide "
        "crisp, mathematically grounded justifications for each design choice."
    )

    # =========================================================================
    # SLIDE 25: Appendix: Technical Specifications & Hyperparameters
    # =========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    setup_slide_chrome(s25, "Appendix", "HoneyComb Technical Specification & Hyperparameters", "Complete reference table of architectural, training, and inference hyperparameters", 25)

    add_bullet_card(s25, Inches(0.8), Inches(1.75), Inches(3.7), Inches(4.9), "Architecture Specifications", [
        ("Spatial Resolution", "128 x 128 x 3 direct RGB pixel space"),
        ("Backbone Topology", "4-level U-Net (128->64->32->16)"),
        ("Filter Multipliers", "Base 32 [1, 2, 4, 8] -> [32, 64, 128, 256]"),
        ("Trainable Parameters", "91,412,483 parameters"),
        ("Text Embedding", "SentenceTransformer 'all-MiniLM-L6-v2' (384-dim)"),
        ("Max Text Tokens", "24 tokens + attention mask + register token"),
        ("Attention Blocks", "Spatial self-attn & cross-attn at 32x32 & 16x16")
    ], title_color=C_GOLD)

    add_bullet_card(s25, Inches(4.8), Inches(1.75), Inches(3.7), Inches(4.9), "Training Hyperparameters", [
        ("Dataset", "MS-COCO 2017 (118,287 training images)"),
        ("Noise Schedule", "Cosine variance schedule (T = 1,000 steps)"),
        ("Loss Objective", "Min-SNR-γ loss weighting (γ = 5.0)"),
        ("Optimizer", "AdamW (lr = 1e-4, weight decay = 1e-4)"),
        ("Gradient Clipping", "Global norm clipped at 1.0"),
        ("EMA Shadow Decay", "β = 0.9999 for shadow weight tracking"),
        ("CFG Dropout", "10% unconditional text embedding dropout")
    ], title_color=C_CYAN)

    add_bullet_card(s25, Inches(8.8), Inches(1.75), Inches(3.7), Inches(4.9), "Inference & Serving Specs", [
        ("Sampling Algorithm", "DDIM (Denoising Diffusion Implicit Models)"),
        ("Inference Steps", "20 to 50 steps (default: 30)"),
        ("Guidance Scale w", "5.0 default (operating range: 1.0 to 10.0)"),
        ("Backend Framework", "FastAPI asynchronous ASGI on Uvicorn"),
        ("Serving Endpoint", "POST /api/generate with base64 PNG response"),
        ("Inference Latency", "~1.8 seconds per batch on local GPU"),
        ("Frontend Stack", "HTML5 Canvas, Vanilla JS, CSS3 Studio Theme")
    ], title_color=C_GREEN)

    s25.notes_slide.notes_text_frame.text = (
        "The appendix provides the complete engineering specifications of HoneyComb across architecture, training hyperparameters, "
        "and inference settings. These exact figures confirm all configuration parameters implemented in the repository."
    )

    # Save to both required destinations
    out1 = "deliverables/CocoCanvas_Presentation.pptx"
    out2 = "deliverables/HoneyComb_Presentation.pptx"

    prs.save(out1)
    prs.save(out2)
    print(f"Presentation saved successfully to:\n  1. {out1}\n  2. {out2}")

if __name__ == "__main__":
    create_full_presentation()
