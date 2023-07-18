export interface SearchResult {
  content_title: string
  content_url: string
  content: string
}

export interface SearchResponse {
  sources: SearchResult[]
}
