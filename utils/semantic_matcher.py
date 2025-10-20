# utils/semantic_matcher.py

from sentence_transformers import SentenceTransformer, util

class SemanticSkillMatcher:
    def __init__(self, model_name='all-MiniLM-L6-v2', threshold=0.7):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

    def match(self, user_skills, job_skills):
        if not user_skills or not job_skills:
            return [], job_skills
        user_emb = self.model.encode(user_skills, convert_to_tensor=True)
        job_emb = self.model.encode(job_skills, convert_to_tensor=True)
        matched = []
        missing = []
        for j, jskill in enumerate(job_skills):
            sim_scores = util.cos_sim(job_emb[j], user_emb)[0]
            if any(sim_scores >= self.threshold):
                matched.append(jskill)
            else:
                missing.append(jskill)
        return matched, missing
