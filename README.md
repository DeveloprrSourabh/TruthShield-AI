# \# TruthShield AI

# 

# TruthShield AI is an AI-based Fake News Detection System that verifies news using multiple verification techniques.

# 

# The system combines:

# 

# \- Artificial Immune System (AIS)

# \- Web Search Verification

# \- Natural Language Processing (NLP)

# \- Decision/Fusion Module

# 

# The system produces one of three final outcomes:

# 

# \- REAL

# \- FAKE

# \- UNCERTAIN

# 

# \---

# 

# \## Project Architecture

# 

# ```text

# &#x20;                   User News

# &#x20;                      |

# &#x20;                      v

# &#x20;                React Frontend

# &#x20;                      |

# &#x20;                      v

# &#x20;                Flask Backend

# &#x20;                      |

# &#x20;                      v

# &#x20;               Decision Module

# &#x20;                      |

# &#x20;         +------------+------------+

# &#x20;         |            |            |

# &#x20;         v            v            v

# &#x20;        AIS       Web Search      NLP

# &#x20;         |            |            |

# &#x20;      AIS Score    Evidence    NLP Score

# &#x20;         |            |       + Relationship

# &#x20;         +------------+------------+

# &#x20;                      |

# &#x20;                      v

# &#x20;                Final Decision

# &#x20;                      |

# &#x20;                      v

# &#x20;             REAL / FAKE / UNCERTAIN

# &#x20;                      |

# &#x20;                      v

# &#x20;                React Frontend

