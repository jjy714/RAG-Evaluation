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
    ) -> List[Dict[str, Any]]:
        
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="DataFrame is empty.",
            )

        samples: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            row_dict = {
                col: ("" if pd.isna(row[col]) else str(row[col]))
                for col in df.columns
            }
            samples.append(row_dict)

        if not samples:
            raise HTTPException(status_code=400, detail="No valid rows in CSV.")
        return samples



    async def receive_rawdata_csv(
        self,
        content: bytes,
        sep: Optional[str] = None,
        encoding: Optional[str] = None,
    ):
        df = self._load_csv_bytes(content, sep=sep, encoding=encoding)
        samples = self._df_to_raw_samples(df)
        return {"samples": samples}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("RecieveData:app", host="0.0.0.0", port=8000, reload=True)