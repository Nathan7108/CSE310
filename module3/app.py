from flask import Flask, request, render_template, jsonify
import difflib
import re
import PyPDF2
import io
from collections import Counter
import math
from nltk.stem import PorterStemmer

app = Flask(__name__)

# Porter stemmer for full word stemming
stemmer = PorterStemmer()

def simple_stem(word):
    """Convert word to base form using NLTK PorterStemmer"""
    return stemmer.stem(word.lower())

def preprocess_text(text):
    """Clean text - lowercase and remove extra spaces"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_words(text):
    """Extract words from text, removing punctuation"""
    return re.findall(r'\b\w+\b', text.lower())

def get_word_frequencies(text):
    """Get word frequency count with stemming"""
    words = extract_words(text)
    stemmed_words = [simple_stem(word) for word in words]
    return Counter(stemmed_words)

def analyze_structure(text):
    """Analyze document structure - paragraphs and organization"""
    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) < 2:
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
    
    structure = []
    for para in paragraphs:
        para_words = extract_words(para)
        if len(para_words) > 0:
            first_words = ' '.join(para_words[:5])
            length_cat = 'short' if len(para_words) < 50 else 'medium' if len(para_words) < 150 else 'long'
            word_freq = Counter([simple_stem(w) for w in para_words])
            top_stem = word_freq.most_common(1)[0][0] if word_freq else ''
            
            structure.append({
                'length': length_cat,
                'first_words': first_words,
                'top_stem': top_stem,
                'word_count': len(para_words)
            })
    
    return structure

def calculate_structural_similarity(structure1, structure2):
    """Compare document structure similarity"""
    if not structure1 or not structure2:
        return 0.0
    
    # Compare paragraph rhythm
    min_len = min(len(structure1), len(structure2))
    if min_len == 0:
        return 0.0
    
    matches = 0
    for i in range(min_len):
        if structure1[i]['length'] == structure2[i]['length']:
            matches += 1
    
    rhythm_score = matches / min_len if min_len > 0 else 0
    
    # Compare word stems
    stems1 = [s['top_stem'] for s in structure1 if s['top_stem']]
    stems2 = [s['top_stem'] for s in structure2 if s['top_stem']]
    common_stems = set(stems1) & set(stems2)
    all_stems = set(stems1) | set(stems2)
    stem_score = len(common_stems) / len(all_stems) if all_stems else 0
    
    # Combined score
    structural_score = (rhythm_score * 0.6 + stem_score * 0.4) * 100
    return structural_score

def calculate_lexical_similarity(text1, text2):
    """Compare word frequency similarity"""
    freq1 = get_word_frequencies(text1)
    freq2 = get_word_frequencies(text2)
    
    if not freq1 or not freq2:
        return 0.0
    
    all_words = set(freq1.keys()) | set(freq2.keys())
    if not all_words:
        return 0.0
    
    # Calculate cosine similarity
    dot_product = sum(freq1.get(word, 0) * freq2.get(word, 0) for word in all_words)
    magnitude1 = math.sqrt(sum(count ** 2 for count in freq1.values()))
    magnitude2 = math.sqrt(sum(count ** 2 for count in freq2.values()))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    cosine_similarity = dot_product / (magnitude1 * magnitude2)
    
    # Word overlap
    common_words = set(freq1.keys()) & set(freq2.keys())
    overlap_ratio = len(common_words) / len(all_words) if all_words else 0
    
    # Combined score
    lexical_score = (cosine_similarity * 0.7 + overlap_ratio * 0.3) * 100
    return lexical_score

def calculate_semantic_similarity(text1, text2):
    """Compare semantic similarity - rephrased ideas"""
    words1 = extract_words(text1)
    words2 = extract_words(text2)
    
    if len(words1) < 10 or len(words2) < 10:
        return 0.0
    
    # Check n-grams (phrases of different lengths)
    similarities = []
    for n in [3, 4, 5]:
        ngrams1 = set()
        ngrams2 = set()
        
        for i in range(len(words1) - n + 1):
            ngram = ' '.join(words1[i:i+n])
            ngrams1.add(ngram)
        
        for i in range(len(words2) - n + 1):
            ngram = ' '.join(words2[i:i+n])
            ngrams2.add(ngram)
        
        if ngrams1 or ngrams2:
            common = len(ngrams1 & ngrams2)
            total = len(ngrams1 | ngrams2)
            if total > 0:
                similarities.append(common / total)
    
    # Check word sequences with stemming
    stemmed1 = [simple_stem(w) for w in words1]
    stemmed2 = [simple_stem(w) for w in words2]
    
    common_sequences = 0
    for i in range(min(len(stemmed1), len(stemmed2)) - 4):
        seq1 = ' '.join(stemmed1[i:i+4])
        if seq1 in ' '.join(stemmed2):
            common_sequences += 1
    
    seq_score = common_sequences / max(len(stemmed1), len(stemmed2)) if stemmed1 or stemmed2 else 0
    
    # Combined score
    avg_ngram = sum(similarities) / len(similarities) if similarities else 0
    semantic_score = (avg_ngram * 0.7 + min(seq_score * 10, 1.0) * 0.3) * 100
    return semantic_score

def calculate_enhanced_similarity(text1, text2):
    """Calculate overall similarity using multiple methods"""
    # Exact text similarity
    sequence_ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
    sequence_score = sequence_ratio * 100
    
    # Structural analysis
    structure1 = analyze_structure(text1)
    structure2 = analyze_structure(text2)
    structural_score = calculate_structural_similarity(structure1, structure2)
    
    # Lexical analysis
    lexical_score = calculate_lexical_similarity(text1, text2)
    
    # Semantic analysis
    semantic_score = calculate_semantic_similarity(text1, text2)
    
    # Weighted combination
    final_score = (
        structural_score * 0.25 +
        lexical_score * 0.30 +
        semantic_score * 0.25 +
        sequence_score * 0.20
    )
    
    return {
        'overall': round(final_score, 2),
        'structural': round(structural_score, 2),
        'lexical': round(lexical_score, 2),
        'semantic': round(semantic_score, 2),
        'sequence': round(sequence_score, 2)
    }

def find_common_phrases(text1, text2, min_length=5):
    """Find phrases that appear in both texts"""
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    words1 = extract_words(text1_lower)
    words2 = extract_words(text2_lower)
    
    common_phrases = []
    seen_phrases = set()
    
    # Check multiple phrase lengths
    for phrase_len in [min_length, min_length+2, min_length+5]:
        if phrase_len > len(words1) or phrase_len > len(words2):
            continue
        
        # Build phrase dictionary from text2 for fast lookup
        phrases2_dict = {}
        for j in range(len(words2) - phrase_len + 1):
            phrase2 = ' '.join(words2[j:j+phrase_len])
            if phrase2 not in phrases2_dict:
                phrases2_dict[phrase2] = []
            phrases2_dict[phrase2].append(j)
        
        # Check phrases from text1
        for i in range(len(words1) - phrase_len + 1):
            phrase1 = ' '.join(words1[i:i+phrase_len])
            
            if phrase1 in phrases2_dict:
                original_words = extract_words(text1)
                if i < len(original_words) and i+phrase_len <= len(original_words):
                    original_phrase = ' '.join(original_words[i:i+phrase_len])
                    phrase_key = phrase1.lower()
                    
                    if phrase_key not in seen_phrases:
                        seen_phrases.add(phrase_key)
                        common_phrases.append(original_phrase)
        
        if len(common_phrases) >= 20:
            break
    
    # Also check with stemming for semantic overlap
    stemmed1 = [simple_stem(w) for w in words1]
    stemmed2 = [simple_stem(w) for w in words2]
    
    for phrase_len in [4, 6]:
        if phrase_len > len(stemmed1) or phrase_len > len(stemmed2):
            continue
        
        stem_phrases2 = set()
        for j in range(len(stemmed2) - phrase_len + 1):
            stem_phrase = ' '.join(stemmed2[j:j+phrase_len])
            stem_phrases2.add(stem_phrase)
        
        for i in range(len(stemmed1) - phrase_len + 1):
            stem_phrase1 = ' '.join(stemmed1[i:i+phrase_len])
            
            if stem_phrase1 in stem_phrases2:
                original_words = extract_words(text1)
                if i < len(original_words) and i+phrase_len <= len(original_words):
                    original_phrase = ' '.join(original_words[i:i+phrase_len])
                    phrase_key = stem_phrase1.lower()
                    
                    if phrase_key not in seen_phrases:
                        seen_phrases.add(phrase_key)
                        common_phrases.append(original_phrase)
    
    return common_phrases[:20]

def find_matching_sections(text1, text2):
    """Find matching sentences between texts"""
    sentences1 = re.split(r'[.!?]+(?:\s+|$)', text1)
    sentences2 = re.split(r'[.!?]+(?:\s+|$)', text2)
    
    sentences1 = [s.strip() for s in sentences1 if len(s.strip()) > 15]
    sentences2 = [s.strip() for s in sentences2 if len(s.strip()) > 15]
    
    matching_pairs = []
    
    for i, sent1 in enumerate(sentences1):
        sent1_lower = sent1.lower()
        sent1_words = extract_words(sent1)
        sent1_stemmed = [simple_stem(w) for w in sent1_words]
        
        best_match = None
        best_similarity = 0
        
        for j, sent2 in enumerate(sentences2):
            sent2_lower = sent2.lower()
            sent2_words = extract_words(sent2)
            sent2_stemmed = [simple_stem(w) for w in sent2_words]
            
            # Method 1: Sequence similarity
            seq_sim = difflib.SequenceMatcher(None, sent1_lower, sent2_lower).ratio()
            
            # Method 2: Word overlap
            common_words = set(sent1_stemmed) & set(sent2_stemmed)
            all_words = set(sent1_stemmed) | set(sent2_stemmed)
            word_sim = len(common_words) / len(all_words) if all_words else 0
            
            # Method 3: N-gram matching
            ngram_sim = 0
            for n in [3, 4, 5]:
                ngrams1 = [' '.join(sent1_stemmed[k:k+n]) for k in range(len(sent1_stemmed)-n+1)]
                ngrams2 = [' '.join(sent2_stemmed[k:k+n]) for k in range(len(sent2_stemmed)-n+1)]
                common_ngrams = set(ngrams1) & set(ngrams2)
                all_ngrams = set(ngrams1) | set(ngrams2)
                if all_ngrams:
                    ngram_ratio = len(common_ngrams) / len(all_ngrams)
                    ngram_sim = max(ngram_sim, ngram_ratio)
            
            # Combined similarity
            combined_sim = (seq_sim * 0.4 + word_sim * 0.4 + ngram_sim * 0.2)
            
            if combined_sim > best_similarity:
                best_similarity = combined_sim
                best_match = {
                    'file1_sentence': sent1,
                    'file2_sentence': sent2,
                    'similarity': combined_sim,
                    'file1_index': i,
                    'file2_index': j
                }
        
        if best_similarity > 0.45:
            matching_pairs.append(best_match)
    
    return matching_pairs

def find_matching_phrases_in_text(text1, text2, min_length=4):
    """Find matching phrases for highlighting"""
    words1 = extract_words(text1.lower())
    words2 = extract_words(text2.lower())
    
    # Limit processing for large files
    MAX_WORDS = 2000
    if len(words1) > MAX_WORDS:
        words1 = words1[:MAX_WORDS]
    if len(words2) > MAX_WORDS:
        words2 = words2[:MAX_WORDS]
    
    stemmed1 = [simple_stem(w) for w in words1]
    stemmed2 = [simple_stem(w) for w in words2]
    
    matching_phrases = []
    seen_phrases = set()
    
    # Use smaller phrase lengths for performance
    phrase_lengths = [min_length, min_length+3, min_length+6] if len(words1) < 500 else [min_length, min_length+3]
    
    for n in phrase_lengths:
        if n > len(stemmed1) or n > len(stemmed2):
            continue
        
        # Build phrase dictionary for fast lookup
        phrases1_dict = {}
        for i in range(len(stemmed1) - n + 1):
            phrase = ' '.join(stemmed1[i:i+n])
            if phrase not in phrases1_dict:
                phrases1_dict[phrase] = []
            phrases1_dict[phrase].append(i)
        
        # Check phrases from text2 against text1
        for j in range(len(stemmed2) - n + 1):
            phrase2 = ' '.join(stemmed2[j:j+n])
            
            if phrase2 in phrases1_dict:
                for i in phrases1_dict[phrase2]:
                    phrase_key = (i, j, n)
                    if phrase_key not in seen_phrases:
                        seen_phrases.add(phrase_key)
                        matching_phrases.append({
                            'file1_phrase': ' '.join(words1[i:i+n]),
                            'file2_phrase': ' '.join(words2[j:j+n]),
                            'file1_start': i,
                            'file1_end': i+n,
                            'file2_start': j,
                            'file2_end': j+n,
                            'similarity': 1.0,
                            'length': n
                        })
                        if len(matching_phrases) >= 100:
                            return matching_phrases
    
    return matching_phrases[:100]

def highlight_matching_text(text1, text2):
    """Prepare text with matching sections highlighted"""
    matching_pairs = find_matching_sections(text1, text2)
    matching_phrases = find_matching_phrases_in_text(text1, text2, min_length=3)
    
    # Split texts into sentences
    sentences1 = re.split(r'([.!?]+(?:\s+|$))', text1)
    sentences2 = re.split(r'([.!?]+(?:\s+|$))', text2)
    
    words1 = extract_words(text1.lower())
    words2 = extract_words(text2.lower())
    
    # Create sentence markers
    text1_sentence_map = {}
    text2_sentence_map = {}
    
    for pair in matching_pairs:
        sent1 = pair['file1_sentence'].lower()
        sent2 = pair['file2_sentence'].lower()
        
        if sent1 not in text1_sentence_map or pair['similarity'] > text1_sentence_map[sent1]['similarity']:
            text1_sentence_map[sent1] = pair
        if sent2 not in text2_sentence_map or pair['similarity'] > text2_sentence_map[sent2]['similarity']:
            text2_sentence_map[sent2] = pair
    
    # Create phrase position markers
    text1_phrase_matches = {}
    text2_phrase_matches = {}
    
    for phrase in matching_phrases:
        for i in range(phrase['file1_start'], min(phrase['file1_end'], len(words1))):
            if i not in text1_phrase_matches or phrase['similarity'] > text1_phrase_matches[i]:
                text1_phrase_matches[i] = phrase['similarity']
        
        for j in range(phrase['file2_start'], min(phrase['file2_end'], len(words2))):
            if j not in text2_phrase_matches or phrase['similarity'] > text2_phrase_matches[j]:
                text2_phrase_matches[j] = phrase['similarity']
    
    def create_display_with_highlights(text, sentences, words, sentence_map, phrase_matches):
        """Create display with sentence and phrase highlighting"""
        display_items = []
        word_idx = 0
        
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                sent = (sentences[i] + sentences[i+1]).strip()
                if len(sent) < 10:
                    continue
                
                sent_lower = sent.lower()
                sent_words = extract_words(sent_lower)
                sent_word_count = len(sent_words)
                
                # Check if sentence matches
                sentence_matched = False
                sentence_similarity = 0
                
                for sent_key, pair_data in sentence_map.items():
                    sim = difflib.SequenceMatcher(None, sent_lower, sent_key).ratio()
                    if sim > 0.7:
                        sentence_matched = True
                        sentence_similarity = pair_data['similarity']
                        break
                
                # Check for phrase matches
                phrase_spans = []
                current_span_start = None
                current_similarity = 0
                
                for w in range(sent_word_count):
                    global_word_idx = word_idx + w
                    if global_word_idx < len(words) and global_word_idx in phrase_matches:
                        if current_span_start is None:
                            current_span_start = w
                            current_similarity = phrase_matches[global_word_idx]
                        else:
                            current_similarity = max(current_similarity, phrase_matches[global_word_idx])
                    else:
                        if current_span_start is not None:
                            phrase_spans.append({
                                'start': current_span_start,
                                'end': w,
                                'similarity': current_similarity
                            })
                            current_span_start = None
                
                if current_span_start is not None:
                    phrase_spans.append({
                        'start': current_span_start,
                        'end': sent_word_count,
                        'similarity': current_similarity
                    })
                
                display_items.append({
                    'text': sent + ' ',
                    'matched': sentence_matched,
                    'similarity': sentence_similarity,
                    'phrase_spans': phrase_spans
                })
                
                word_idx += sent_word_count
        
        return display_items
    
    display1 = create_display_with_highlights(text1, sentences1, words1, text1_sentence_map, text1_phrase_matches)
    display2 = create_display_with_highlights(text2, sentences2, words2, text2_sentence_map, text2_phrase_matches)
    
    return {
        'file1_sentences': display1,
        'file2_sentences': display2,
        'matches': matching_pairs[:30],
        'phrases': matching_phrases[:50]
    }

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def read_file_content(file):
    """Read content from file - handles text and PDF"""
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    else:
        try:
            return file.read().decode('utf-8')
        except UnicodeDecodeError:
            file.seek(0)
            return file.read().decode('latin-1')

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    """Compare two text files and return similarity results"""
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'Please upload both files'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'Please select both files'}), 400
        
        # Read file contents
        text1 = read_file_content(file1)
        text2 = read_file_content(file2)
        
        # Preprocess texts
        processed_text1 = preprocess_text(text1)
        processed_text2 = preprocess_text(text2)
        
        # Calculate similarity with breakdown
        similarity_breakdown = calculate_enhanced_similarity(processed_text1, processed_text2)
        similarity_score = similarity_breakdown['overall']
        
        # Find common phrases
        common_phrases = find_common_phrases(processed_text1, processed_text2)
        
        # Get highlighted matching sections
        try:
            matching_sections = highlight_matching_text(text1, text2)
        except Exception as e:
            print(f"Error in highlight_matching_text: {str(e)}")
            matching_sections = {
                'file1_sentences': [{'text': text1[:200] + '...', 'matched': False, 'similarity': 0}],
                'file2_sentences': [{'text': text2[:200] + '...', 'matched': False, 'similarity': 0}],
                'matches': [],
                'phrases': []
            }
        
        return jsonify({
            'similarity': round(similarity_score, 2),
            'similarity_breakdown': similarity_breakdown,
            'common_phrases': common_phrases,
            'matching_sections': matching_sections,
            'original_text1': text1,
            'original_text2': text2
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in compare: {error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
