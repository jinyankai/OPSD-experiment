# 30-Minute Survey Presentation Outline

Audience: ML-literate research group / lab members.

## Main Deck

1. **Title and Question**  
   Bullets: self-distillation; on-policy distillation; why post-training credit assignment matters.  
   Visual: triangle of SFT, RLVR, OPD.  
   Notes: Frame the talk as a search for dense feedback on the model's own states.  
   Time: 1 min.

2. **Why Off-Policy KD Is Not Enough**  
   Bullets: exposure bias; teacher traces not student states; compounding errors.  
   Visual: train trajectory vs inference trajectory.  
   Notes: Distillation data can be excellent but still irrelevant to the errors the student actually makes.  
   Time: 1.2 min.

3. **Why RLVR Is Not Enough**  
   Bullets: sparse outcome reward; high rollout cost; all-correct/all-wrong batches.  
   Visual: sequence reward vs token feedback.  
   Notes: RLVR is on-policy but often starves the optimizer of local credit assignment.  
   Time: 1.2 min.

4. **OPD: Best of Both Worlds**  
   Bullets: student rollout; teacher token scoring; dense + on-policy.  
   Visual: Thinking Machines chess analogy / token grader.  
   Notes: OPD asks the teacher to grade the student's own moves, not demonstrate a perfect game.  
   Time: 1.3 min.

5. **Foundations: GKD and MiniLLM**  
   Bullets: GKD self-generated mistakes; reverse-KL; generative KD.  
   Visual: loss comparison.  
   Notes: These works give the mathematical vocabulary for later 2026 methods.  
   Time: 1.4 min.

6. **Taxonomy**  
   Bullets: teacher source; information asymmetry; objective; granularity; domain.  
   Visual: matrix.  
   Notes: Use taxonomy to stop the talk from becoming a paper list.  
   Time: 1.4 min.

7. **OPCD: Context as Teacher Advantage**  
   Bullets: context-free student; context-conditioned teacher; reverse-KL.  
   Visual: context distilled into weights.  
   Notes: OPCD moves from model compression to context internalization.  
   Time: 1.5 min.

8. **Experiential Learning Line**  
   Bullets: experience extraction; accumulation; consolidation; online loop.  
   Visual: OEL loop.  
   Notes: Experience can be treated as a reusable context that later becomes parameters.  
   Time: 1.5 min.

9. **OPSD: One Model, Two Contexts**  
   Bullets: student sees question; teacher sees privileged solution; shared base model.  
   Visual: OPSD prompt split.  
   Notes: The teacher is not larger; it is better informed.  
   Time: 1.7 min.

10. **OPSD Objective**  
    Bullets: on-policy rollout; full-vocab JSD; sampled-token alternative; fixed teacher.  
    Visual: JSD equation and stop-gradient arrow.  
    Notes: Clarify reverse-KL/JSD/sample-token tradeoff.  
    Time: 1.8 min.

11. **OPSD Results and Reproduction Target**  
    Bullets: math benchmarks; 1 rollout vs GRPO 8 rollouts; token efficiency claim.  
    Visual: table placeholder plus source label.  
    Notes: Mark paper/README results as claims until reproduced.  
    Time: 1.5 min.

12. **SDPO: Feedback-Conditioned Self-Teacher**  
    Bullets: rich textual feedback; no external teacher; dense signal from feedback context.  
    Visual: failed attempt + runtime feedback -> teacher distribution.  
    Notes: SDPO sits closest to RLVR and tool/code environments.  
    Time: 1.6 min.

13. **OPCD vs OPSD vs SDPO**  
    Bullets: context; privileged trace; feedback; same template.  
    Visual: three-row comparison.  
    Notes: The shared abstraction is conditional self/teacher distribution over student rollouts.  
    Time: 1.4 min.

14. **Failure Mode: Support Mismatch**  
    Bullets: student prefixes drift; teacher unreliable; sampled-token fragility.  
    Visual: prefix outside teacher support.  
    Notes: On-policy does not make teacher feedback automatically trustworthy.  
    Time: 1.3 min.

15. **Failure Mode: Uncertainty Suppression**  
    Bullets: shorter reasoning; less epistemic verbalization; OOD degradation.  
    Visual: uncertainty tokens disappearing.  
    Notes: Privileged context can teach confidence, not just correctness.  
    Time: 1.3 min.

16. **Failure Mode: Style-Token Domination**  
    Bullets: high KL on style tokens; collapse risk; clipping.  
    Visual: token KL histogram.  
    Notes: OPSD repo explicitly adds point-wise KL/JSD clipping for this.  
    Time: 1.2 min.

17. **2026 Fixes: Local Support and Entropy**  
    Bullets: teacher top-K support; special-token masking; entropy-aware KL mixing.  
    Visual: top-K truncation.  
    Notes: The theme is selective trust in teacher distributions.  
    Time: 1.5 min.

18. **2026 Fixes: RLSD and SRPO**  
    Bullets: RLVR direction; distillation magnitude; sample routing.  
    Visual: correct -> GRPO, failed -> SDPO.  
    Notes: Hybrid methods stop asking self-distillation to do everything.  
    Time: 1.6 min.

19. **Black-Box and Semi-On-Policy Branch**  
    Bullets: no logits; adversarial reward; static student contrast.  
    Visual: GAD/SODA pipeline.  
    Notes: Useful when frontier teacher internals are unavailable.  
    Time: 1.2 min.

20. **Open Problems**  
    Bullets: teacher uncertainty; PI leakage; agent memory; long-horizon credit; reproducible eval.  
    Visual: open problem map.  
    Notes: Emphasize where a research project can contribute.  
    Time: 1.5 min.

21. **Takeaways**  
    Bullets: dense on-policy feedback; information asymmetry; selective trust.  
    Visual: final taxonomy with highlighted path.  
    Notes: Close with three design rules for future OPD systems.  
    Time: 1 min.

## Backup Slides

- Formula sheet: forward-KL, reverse-KL, generalized JSD, sampled-token log-ratio.
- Full comparison matrix.
- OPSD repository map.
- Reproduction commands.
- Failure-mode paper details.
- Q&A: self-distillation without privileged context, boundary with RLVR, why shorter reasoning can hurt.
