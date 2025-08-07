import re
import string
from typing import List, Dict, Set
from collections import Counter
import logging

log = logging.getLogger(__name__)

# Stopwords em múltiplos idiomas
STOPWORDS = {
    'pt': {
        'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
        'por', 'para', 'com', 'sem', 'sob', 'sobre', 'entre', 'até', 'após', 'desde', 'durante',
        'e', 'é', 'ou', 'mas', 'porém', 'todavia', 'contudo', 'entretanto', 'que', 'se', 'como', 'quando',
        'onde', 'quem', 'qual', 'quanto', 'isso', 'isto', 'aquilo', 'esse', 'este', 'aquele', 'essa', 'esta',
        'aquela', 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'me', 'te', 'se', 'nos', 'vos',
        'meu', 'teu', 'seu', 'nossa', 'vossa', 'sua', 'minha', 'tua', 'suas', 'muito', 'pouco', 'mais', 'menos',
        'já', 'ainda', 'sempre', 'nunca', 'também', 'só', 'apenas', 'bem', 'mal', 'sim', 'não', 'talvez',
        'foi', 'ser', 'ter', 'estar', 'fazer', 'ir', 'vir', 'ver', 'dar', 'saber', 'poder', 'querer'
    },
    'en': {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as',
        'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
        'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'just', 'if', 'then', 'else', 'there', 'here', 'their', 'your', 'our', 'my', 'his', 'her',
        'its', 'am', 'because', 'after', 'before', 'while', 'during', 'about', 'against', 'between', 'into',
        'through', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'once'
    }
}

# Palavras-chave por categoria/domínio
DOMAIN_KEYWORDS = {
    'programação': {
        'keywords': ['código', 'code', 'programação', 'programming', 'algoritmo', 'algorithm', 'função', 'function',
                     'classe', 'class', 'método', 'method', 'variável', 'variable', 'loop', 'array', 'lista', 'list',
                     'api', 'backend', 'frontend', 'database', 'banco de dados', 'sql', 'javascript', 'python', 'java',
                     'react', 'vue', 'angular', 'node', 'npm', 'git', 'github', 'debug', 'erro', 'error', 'bug'],
        'tag': 'desenvolvimento'
    },
    'inteligência artificial': {
        'keywords': ['ia', 'ai', 'inteligência artificial', 'artificial intelligence', 'machine learning',
                     'aprendizado de máquina', 'deep learning', 'neural', 'rede neural', 'neural network',
                     'modelo', 'model', 'treinamento', 'training', 'dataset', 'dados', 'data', 'tensor',
                     'pytorch', 'tensorflow', 'sklearn', 'nlp', 'processamento de linguagem', 'gpt', 'llm',
                     'transformer', 'bert', 'classificação', 'classification', 'regressão', 'regression'],
        'tag': 'ai-ml'
    },
    'negócios': {
        'keywords': ['negócio', 'business', 'empresa', 'company', 'cliente', 'client', 'customer', 'vendas', 'sales',
                     'marketing', 'estratégia', 'strategy', 'planejamento', 'planning', 'meta', 'goal', 'objetivo',
                     'kpi', 'roi', 'receita', 'revenue', 'lucro', 'profit', 'custo', 'cost', 'investimento',
                     'investment', 'mercado', 'market', 'concorrência', 'competition', 'produto', 'product'],
        'tag': 'business'
    },
    'design': {
        'keywords': ['design', 'ui', 'ux', 'interface', 'usuário', 'user', 'experiência', 'experience', 'layout',
                     'cor', 'color', 'tipografia', 'typography', 'fonte', 'font', 'ícone', 'icon', 'botão', 'button',
                     'formulário', 'form', 'navegação', 'navigation', 'wireframe', 'mockup', 'prototipo', 'prototype',
                     'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'responsive', 'responsivo', 'mobile'],
        'tag': 'design'
    },
    'educação': {
        'keywords': ['aprender', 'learn', 'estudar', 'study', 'curso', 'course', 'aula', 'class', 'lesson',
                     'professor', 'teacher', 'aluno', 'student', 'escola', 'school', 'universidade', 'university',
                     'educação', 'education', 'ensino', 'teaching', 'conhecimento', 'knowledge', 'livro', 'book',
                     'artigo', 'article', 'pesquisa', 'research', 'tese', 'thesis', 'dissertação', 'dissertation'],
        'tag': 'educação'
    },
    'saúde': {
        'keywords': ['saúde', 'health', 'medicina', 'medicine', 'médico', 'doctor', 'paciente', 'patient',
                     'tratamento', 'treatment', 'doença', 'disease', 'sintoma', 'symptom', 'diagnóstico', 'diagnosis',
                     'remédio', 'medicamento', 'medication', 'hospital', 'clínica', 'clinic', 'exame', 'exam',
                     'cirurgia', 'surgery', 'terapia', 'therapy', 'vacina', 'vaccine', 'prevenção', 'prevention'],
        'tag': 'saúde'
    },
    'finanças': {
        'keywords': ['dinheiro', 'money', 'finanças', 'finance', 'investimento', 'investment', 'ação', 'stock',
                     'bolsa', 'mercado financeiro', 'banco', 'bank', 'crédito', 'credit', 'débito', 'debit',
                     'poupança', 'savings', 'juros', 'interest', 'taxa', 'rate', 'inflação', 'inflation',
                     'bitcoin', 'crypto', 'criptomoeda', 'cryptocurrency', 'carteira', 'wallet', 'renda', 'income'],
        'tag': 'finanças'
    },
    'projeto': {
        'keywords': ['projeto', 'project', 'tarefa', 'task', 'prazo', 'deadline', 'entrega', 'delivery',
                     'milestone', 'sprint', 'agile', 'scrum', 'kanban', 'backlog', 'roadmap', 'timeline',
                     'equipe', 'team', 'colaboração', 'collaboration', 'reunião', 'meeting', 'status', 'progresso',
                     'progress', 'risco', 'risk', 'issue', 'problema', 'solução', 'solution'],
        'tag': 'projeto'
    },
    'pessoal': {
        'keywords': ['pessoal', 'personal', 'vida', 'life', 'família', 'family', 'amigo', 'friend', 'casa', 'home',
                     'hobby', 'lazer', 'leisure', 'viagem', 'travel', 'férias', 'vacation', 'aniversário', 'birthday',
                     'relacionamento', 'relationship', 'amor', 'love', 'felicidade', 'happiness', 'bem-estar', 'wellbeing'],
        'tag': 'pessoal'
    },
    'todo': {
        'keywords': ['todo', 'fazer', 'pendente', 'pending', 'tarefa', 'task', 'lista', 'list', 'checklist',
                     'lembrete', 'reminder', 'importante', 'important', 'urgente', 'urgent', 'prioridade', 'priority',
                     'completar', 'complete', 'concluir', 'finish', 'realizar', 'accomplish'],
        'tag': 'todo'
    },
    'ideia': {
        'keywords': ['ideia', 'idea', 'conceito', 'concept', 'pensamento', 'thought', 'insight', 'inspiração',
                     'inspiration', 'criatividade', 'creativity', 'inovação', 'innovation', 'brainstorm',
                     'possibilidade', 'possibility', 'oportunidade', 'opportunity', 'sugestão', 'suggestion'],
        'tag': 'ideia'
    },
    'referência': {
        'keywords': ['referência', 'reference', 'link', 'url', 'fonte', 'source', 'bibliografia', 'bibliography',
                     'citação', 'citation', 'documentação', 'documentation', 'manual', 'guide', 'tutorial',
                     'exemplo', 'example', 'recurso', 'resource', 'material', 'conteúdo', 'content'],
        'tag': 'referência'
    }
}

# Expressões e padrões para identificar conteúdo
CONTENT_PATTERNS = {
    'código': r'```[\s\S]*?```|`[^`]+`|function\s+\w+|class\s+\w+|def\s+\w+|const\s+\w+|let\s+\w+|var\s+\w+',
    'url': r'https?://[^\s]+',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'data': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
    'número': r'\b\d+([.,]\d+)?\b',
    'lista': r'^[\s]*[-*+•]\s+.+$',
    'título': r'^#{1,6}\s+.+$|^.+\n[=-]+$'
}


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extrai palavras-chave relevantes do texto.
    """
    # Converter para minúsculas
    text_lower = text.lower()
    
    # Remover URLs, emails e código
    text_clean = re.sub(CONTENT_PATTERNS['url'], '', text_lower)
    text_clean = re.sub(CONTENT_PATTERNS['email'], '', text_clean)
    text_clean = re.sub(CONTENT_PATTERNS['código'], '', text_clean)
    text_clean = re.sub(r'[^\w\s-]', ' ', text_clean)
    
    # Tokenizar
    words = text_clean.split()
    
    # Combinar stopwords de múltiplos idiomas
    all_stopwords = set()
    for lang_stopwords in STOPWORDS.values():
        all_stopwords.update(lang_stopwords)
    
    # Filtrar stopwords e palavras muito curtas
    filtered_words = [
        word for word in words 
        if word not in all_stopwords 
        and len(word) > 2
        and not word.isdigit()
    ]
    
    # Contar frequência
    word_freq = Counter(filtered_words)
    
    # Pegar as palavras mais frequentes
    keywords = [word for word, _ in word_freq.most_common(max_keywords)]
    
    return keywords


def identify_domains(text: str) -> Set[str]:
    """
    Identifica domínios/categorias baseado no conteúdo.
    """
    text_lower = text.lower()
    identified_domains = set()
    
    for domain, info in DOMAIN_KEYWORDS.items():
        keywords = info['keywords']
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Se encontrar pelo menos 3 palavras-chave do domínio
        if matches >= 3:
            identified_domains.add(info['tag'])
    
    return identified_domains


def detect_content_type(text: str) -> Set[str]:
    """
    Detecta tipos de conteúdo especiais.
    """
    content_types = set()
    
    # Verificar se contém código
    if re.search(CONTENT_PATTERNS['código'], text):
        content_types.add('código')
    
    # Verificar se contém muitos links
    urls = re.findall(CONTENT_PATTERNS['url'], text)
    if len(urls) >= 3:
        content_types.add('links')
    
    # Verificar se é uma lista
    lines = text.split('\n')
    list_lines = [line for line in lines if re.match(CONTENT_PATTERNS['lista'], line)]
    if len(list_lines) >= 3:
        content_types.add('lista')
    
    # Verificar se tem estrutura de documento (títulos)
    title_lines = [line for line in lines if re.match(CONTENT_PATTERNS['título'], line)]
    if len(title_lines) >= 2:
        content_types.add('documento')
    
    return content_types


def extract_entities(text: str) -> Set[str]:
    """
    Extrai entidades nomeadas (nomes próprios, tecnologias, etc).
    """
    entities = set()
    
    # Padrões para tecnologias conhecidas
    tech_patterns = [
        r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Ruby|Go|Rust|Swift|Kotlin)\b',
        r'\b(React|Vue|Angular|Next\.js|Nuxt|Svelte|Express|Django|Flask|FastAPI)\b',
        r'\b(Docker|Kubernetes|AWS|Azure|GCP|Git|GitHub|GitLab|Jenkins)\b',
        r'\b(PostgreSQL|MySQL|MongoDB|Redis|SQLite|Oracle|SQL Server)\b',
        r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Jupyter)\b',
        r'\b(HTML|CSS|SASS|SCSS|Tailwind|Bootstrap|Material.UI)\b',
        r'\b(REST|GraphQL|WebSocket|HTTP|HTTPS|API|JSON|XML)\b',
        r'\b(Linux|Windows|macOS|Ubuntu|Debian|CentOS|Android|iOS)\b'
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities.update([m.lower() for m in matches])
    
    # Palavras que começam com maiúscula (possíveis nomes próprios)
    proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    # Filtrar apenas se aparecem mais de uma vez
    proper_noun_counts = Counter(proper_nouns)
    for noun, count in proper_noun_counts.items():
        if count >= 2 and len(noun) > 3:
            entities.add(noun.lower())
    
    return entities


def generate_semantic_tags(title: str, content: str, max_tags: int = 10) -> List[str]:
    """
    Gera tags semânticas baseadas no título e conteúdo da nota.
    
    Args:
        title: Título da nota
        content: Conteúdo da nota (markdown)
        max_tags: Número máximo de tags a gerar
    
    Returns:
        Lista de tags sugeridas
    """
    try:
        tags = set()
        
        # Combinar título e conteúdo para análise
        full_text = f"{title}\n\n{content}"
        
        # 1. Identificar domínios/categorias
        domains = identify_domains(full_text)
        tags.update(domains)
        
        # 2. Detectar tipos de conteúdo
        content_types = detect_content_type(content)
        tags.update(content_types)
        
        # 3. Extrair entidades nomeadas (tecnologias, ferramentas, etc)
        entities = extract_entities(full_text)
        # Limitar entidades às mais relevantes
        if entities:
            # Priorizar entidades que aparecem no título
            title_entities = [e for e in entities if e in title.lower()]
            tags.update(title_entities[:3])
            
            # Adicionar outras entidades se houver espaço
            other_entities = [e for e in entities if e not in title_entities]
            remaining_slots = max_tags - len(tags)
            if remaining_slots > 0:
                tags.update(other_entities[:min(2, remaining_slots)])
        
        # 4. Extrair palavras-chave se ainda houver espaço
        if len(tags) < max_tags:
            keywords = extract_keywords(full_text, max_keywords=5)
            # Filtrar keywords que sejam substantivas e relevantes
            meaningful_keywords = []
            for keyword in keywords:
                # Pular se já está nas tags
                if keyword in tags:
                    continue
                # Pular palavras muito genéricas
                if keyword in {'usar', 'fazer', 'ter', 'ser', 'criar', 'novo', 'pode', 'deve', 'precisa'}:
                    continue
                # Adicionar se for substantivo relevante
                if len(keyword) >= 4:
                    meaningful_keywords.append(keyword)
            
            remaining_slots = max_tags - len(tags)
            tags.update(meaningful_keywords[:remaining_slots])
        
        # 5. Tags especiais baseadas em padrões
        # Se tem muitas perguntas, adicionar tag "dúvida"
        if content.count('?') >= 3:
            tags.add('dúvida')
        
        # Se tem data no futuro próximo, pode ser um lembrete
        if re.search(r'\b(amanhã|tomorrow|próxim[ao]|next)\b', full_text, re.IGNORECASE):
            tags.add('lembrete')
        
        # Se menciona urgência
        if re.search(r'\b(urgente|urgent|asap|importante|important|crítico|critical)\b', full_text, re.IGNORECASE):
            tags.add('importante')
        
        # Converter para lista e limitar ao máximo
        final_tags = list(tags)[:max_tags]
        
        # Garantir pelo menos uma tag
        if not final_tags and len(extract_keywords(full_text, 3)) > 0:
            final_tags = extract_keywords(full_text, 3)[:2]
        
        return final_tags
        
    except Exception as e:
        log.error(f"Error generating semantic tags: {e}")
        return []


def suggest_related_tags(existing_tags: List[str], all_user_tags: List[str]) -> List[str]:
    """
    Sugere tags relacionadas baseadas em tags existentes e tags do usuário.
    
    Args:
        existing_tags: Tags já aplicadas à nota
        all_user_tags: Todas as tags do usuário
    
    Returns:
        Lista de tags relacionadas sugeridas
    """
    suggestions = []
    
    # Mapeamento de tags relacionadas
    related_tags = {
        'desenvolvimento': ['código', 'programação', 'git', 'debug'],
        'ai-ml': ['python', 'dados', 'modelo', 'treinamento'],
        'business': ['estratégia', 'meta', 'projeto', 'reunião'],
        'design': ['ui-ux', 'interface', 'prototipo', 'wireframe'],
        'projeto': ['tarefa', 'prazo', 'equipe', 'milestone'],
        'todo': ['importante', 'urgente', 'lembrete', 'pendente'],
        'ideia': ['conceito', 'brainstorm', 'inovação', 'proposta'],
        'código': ['desenvolvimento', 'git', 'review', 'bug'],
        'documento': ['referência', 'manual', 'guia', 'especificação'],
        'reunião': ['ata', 'decisão', 'ação', 'follow-up']
    }
    
    for tag in existing_tags:
        if tag in related_tags:
            for related in related_tags[tag]:
                if related not in existing_tags and related in all_user_tags:
                    suggestions.append(related)
    
    return list(set(suggestions))[:5]  # Retornar até 5 sugestões