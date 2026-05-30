from pydantic import (BaseModel , Field , AnyUrl , field_validator , model_validator , computed_field , EmailStr )
from typing import Annotated , Literal , Optional,List
from uuid import UUID
from datetime import datetime

# CREATE PYDANTIC

class Seller (BaseModel):
    seller_id : UUID
    seller_name : Annotated[
        str,
        Field(
            min_length=6,
            max_length= 30 ,
            title ="seller name",
            examples=["apple store","mi store"]
        ),
    ]
    email : EmailStr
    website : AnyUrl
    @field_validator("email",mode="after")
    @classmethod
    def validateEmaillDomain(cls,value :EmailStr):
        allowedDomain = ["mistore.in" , "hpworld.in"]
        domain = str(value).split("@")[-1]
        if domain not in allowedDomain:
            raise ValueError(f"seller email domain not allowed : {domain}")
        return value

class Dimension_CM (BaseModel):
    length : Annotated[
        float,
        Field(
            ge = 0,
            strict = True ,
            description = "product length in cm"
        ),
    ]
    width : Annotated[
        float,
        Field(
            ge = 0,
            strict = True ,
            description = "product width in cm"
        ),
    ]
    height : Annotated[
        float,
        Field(
            ge = 0,
            strict = True ,
            description = "product height in cm"
        ),
    ]

class Product(BaseModel):
    id : UUID
    sku : Annotated[
        str,
        Field(
            min_length=6,
            max_length= 30 ,
            title ="SKU",
            description="stock keeping units",
            examples=["xiao-345633-998","appl-,212gv-049"]
        ),
    ]
    name : Annotated[
        str,
        Field(
            min_length=3,
            max_length= 80 ,
            title ="product name",
            description="readable product name(3-80chars)",
            examples=["xiamo model pro","apple model x"]
        ),
    ]
    description : Annotated[
        str,
        Field(
            max_length=200 ,
            description="short product description",
        ),
    ]
    category : Annotated[
        str,
        Field(
            min_length=3,
            max_length= 30 ,
            description="category like homeware , laptop",
            examples=["mobiles" , "laptop"],
        ),
    ]
    brand : Annotated[
        str ,
        Field(
            min_length= 2 ,
            max_length=40,
            examples=["xiomi","apple"],
        )
    ]
    price: Annotated[
        float ,
        Field(
            gt= 0 ,
            strict = True,
            description="base price(INR)",
        )
    ]
    currency : Literal["INR"] = "INR"
    discountPrice:Annotated[
        int , 
        Field(
            ge = 0 ,
            le = 90,
            description="discount in percent(0-90%)",
        ),
    ]=0
    stock : Annotated[
        int ,
        Field(
            ge = 0 ,
            description = "available stock(>=0)",
        ),
    ]
    isActive : Annotated[
        bool,
        Field(
            description="is product active?",
        ),
    ]
    rating: Annotated[
        float,
        Field(
            ge = 0 ,
            le = 5 ,
            strict=True,
            description="rating out of 5",
        ),
    ]
    tags: Annotated[
        Optional[List[str]],
        Field(
            default = None ,
            max_length = 10,
            description="no more than 10 tags",
        ),
    ]
    image: Annotated[
       List[AnyUrl],
        Field(
            max_length = 1,
            description="atleast one image url",
        ),
    ]
    # dimension_cm
    dimension_cm : Dimension_CM

    # seller
    seller : Seller
    created_at : datetime

    @field_validator("sku",mode="after")
    @classmethod
    def validateSkuFormat(cls,value :str):
        if "-" not in value:
            raise ValueError ("sku must have '-'")
        
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError ("sku must end with 3 digts like -987")
        return value

    @model_validator(mode = "after")
    @classmethod
    def validateBusinessRule(cls,model:"Product"):
        if model.stock == 0 and model.isActive is True :
            raise ValueError ("if stock is zero isactive must to false")
        if model.discountPrice > 0 and model.rating == 0:
            raise ValueError ("discounted product must have a rating(rating!=0)")
        return model

    @computed_field
    @property
    def finalPrice(self)->float:
        return round(self.price *(1-self.discountPrice /100),2)

    @computed_field
    @property
    def volume(self)->float:
        d = self.dimension_cm
        return round(d.length * d.width * d.height,2)
    
#UPDATE PYDANTIC

class Dimension_CMUpdate(BaseModel):
    length : Optional[float]= Field(default = None ,gt = 0)
    width : Optional[float] = Field(default = None ,gt = 0)
    height : Optional[float] = Field(default = None ,gt = 0)

class SellerUpdate(BaseModel):
    seller_name : Optional[str] = Field(default = None ,min_length= 2 ,max_length=60)
    email :Optional[EmailStr]= None
    website : Optional[AnyUrl]= None
    @field_validator("email",mode="after")
    @classmethod
    def validateEmaillDomain(cls,value :EmailStr):
        if value is None :
            return value
        allowedDomain ={
            "mistore.in",
            "realmeofficial.in",
            "samsungindia.in",
            "lenovostore.in",
            "hpworld.in",
            "applestoreindia.in",
            "dellexclusive.in",
            "sonycenter.in",
            "oneplusstore.in",
            "asusexclusive.in",  
        }
        domain = str(value).split("@")[-1]
        if domain not in allowedDomain:
            raise ValueError(f"seller email domain not allowed : {domain}")
        return value

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name : Optional[str] = Field(default = None , min_length= 3 , max_length=80)
    description : Optional[str] = Field(default = None, max_length=200)
    category : Optional[str]= None
    brand : Optional[str] = None
    price : Optional[float] = Field(default = None ,gt = 0)
    currency: Optional[Literal["INR"]]= None
    discountPrice : Optional[int] = Field(default = None ,ge= 0 , le = 90)
    stock :Optional[int]= Field(default = None ,ge= 0)
    isActive : Optional[bool]= None
    rating : Optional[float] = Field(default = None ,ge=0, le=5)
    tags : Optional[List[str]] = Field(default = None ,max_length= 10)
    image : Optional[List[AnyUrl]]= None
    dimension_cm : Optional[Dimension_CMUpdate]=None
    seller : Optional[SellerUpdate]= None
    @field_validator("sku",mode="after")
    @classmethod
    def validateSkuFormat(cls,value :str):
        if value is None :
            return value
        if "-" not in value:
            raise ValueError ("sku must have '-'")
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError ("sku must end with 3 digts like -987")
        return value

    @model_validator(mode = "after")
    def validateBusinessRule(self):
        if self.stock is not None and self.isActive is not None :
            if self.stock == 0 and self.isActive is True :
                raise ValueError ("if stock is zero isactive must to false")

        if self.discountPrice is not None and self.rating is not None:  
            if self.discountPrice > 0 and self.rating == 0:
                raise ValueError ("discounted product must have a rating(rating!=0)")

        return self
    

