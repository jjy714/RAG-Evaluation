from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Request
from typing import List, Dict, Any, Optional
import pandas as pd
from io import BytesIO, StringIO
from langchain_core.documents import Document
import chardet  # pip install chardet


class DataReceiver:
    def __init__(self):
        self.router = APIRouter()
        # CSV 파일로 업로드 받는다고 가정
        self.router.add_api_route("/get-raw", self.receive_rawdata_csv, methods=["POST"])
        self.app = FastAPI(title="DataReceiver")
        self.app.include_router(self.router)

    def _load_csv_bytes(
            self,
            content: bytes,
            encoding: Optional[str] = None,
            **read_csv_kwargs
        ) -> pd.DataFrame:
  
        if encoding is None:
            detect = chardet.detect(content) if content else {"encoding": None}
            encoding = detect.get("encoding") or "utf-8"

        text = content.decode(encoding=encoding, errors="replace")

        try:
            df = pd.read_csv(StringIO(text), **read_csv_kwargs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"파일 read 실패: {e}")

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV is empty.")
        return df

    def _df_to_raw_samples(
        self,
        df: pd.DataFrame,
        col_doc: str,
        col_query: str,
        ) -> List[Dict[str, Any]]:
        
        if col_doc not in df.columns or col_query not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"column '{col_doc}' and '{col_query}가 data에 존재하지 않습니다.'. Columns={list(df.columns)}",
            )

        samples: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            page_content = "" if pd.isna(row[col_doc]) else str(row[col_doc])
            query = "" if pd.isna(row[col_query]) else str(row[col_query])

            samples.append(
                {
                    "document": [Document(page_content=page_content)],
                    "query": query,
                }
            )
        if not samples:
            raise HTTPException(status_code=400, detail="No valid rows in CSV.")
        return samples


    async def receive_rawdata_csv(
        self,
        content: bytes,
        col_doc: str = "document",
        col_query: str = "question",
        sep: Optional[str] = None,
        encoding: Optional[str] = None,
    ):
        df = self._load_csv_bytes(content, sep=sep, encoding=encoding)
        samples = self._df_to_raw_samples(df, col_doc=col_doc, col_query=col_query)
        return {"samples": samples}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("RecieveData:app", host="0.0.0.0", port=8000, reload=True)