# -*- coding: UTF-8 -*-
import json
import yaml

class OpenManulDataService:
    """OpenManul Data Service Class for OpenManulServer"""
    def __init__(self, path):
        self.zoos = {}
        
        filename = "/".join([path, "data", "zoo", "names.yaml"])
        with open(filename, encoding="utf8") as f:
            zoos = yaml.safe_load(f)
            for zoo in zoos:
                zoo_id = zoo["ID"]
                if zoo_id in self.zoos: raise Exception(f"repeated zoo ID: {zoo_id}")
                self.zoos[zoo_id] = zoo
        
        filename = "/".join([path, "data", "zoo", "information.yaml"])
        with open(filename, encoding="utf8") as f:
            zoo_infos = yaml.safe_load(f)
            for zoo_info in zoo_infos:
                zoo_id = zoo_info["ID"]
                if zoo_id not in self.zoos: raise Exception(f"zoo ID not found: {zoo_id}")
                for k in zoo_info:
                    self.zoos[zoo_id][k] = zoo_info[k]
        
        self.manuls = {}
        
        filename = "/".join([path, "data", "individuals", "manul", "names.yaml"])
        with open(filename, encoding="utf8") as f:
            names = yaml.safe_load(f)
            for name in names:
                manul_id = name["ID"]
                if manul_id in self.manuls: raise Exception(f"repeated manul ID: {manul_id}")
                self.manuls[manul_id] = name
        
        filename = "/".join([path, "data", "individuals", "manul", "information.yaml"])
        with open(filename, encoding="utf8") as f:
            infos = yaml.safe_load(f)
            for info in infos:
                manul_id = info["ID"]
                if manul_id not in self.manuls: raise Exception(f"manul ID not found: {manul_id}")
                for k in info:
                    self.manuls[manul_id][k] = info[k]
        
        self.image_credits = {}
        
        filename = "/".join([path, "data", "individuals", "manul", "image_credit.yaml"])
        with open(filename, encoding="utf8") as f:
            images = yaml.safe_load(f)
            for img in images:
                image_id = img["ImgID"]
                if image_id in self.image_credits: raise Exception(f"repeated image ID: {image_id}")
                self.image_credits[image_id] = img
                manul_id = "_".join(image_id.split("_")[:-1])
                if manul_id in self.manuls:
                    if "ImgID" not in self.manuls[manul_id]:
                        self.manuls[manul_id]["ImgID"] = image_id
                        self.manuls[manul_id]["ImgAuthor"] = img.get("author","")
                        self.manuls[manul_id]["ImgLink"] = img.get("link",".")
                else:
                    raise Exception(f"image ({image_id}) belongs to unknown manul ID: {manul_id}")
        
        self.litters = {}
        
        filename = "/".join([path, "data", "individuals", "manul", "litters.yaml"])
        with open(filename, encoding="utf8") as f:
            litters = yaml.safe_load(f)
            for litter in litters:
                litter_id = litter["ID"]
                mother_id = litter.get("mother")
                if mother_id and mother_id not in self.manuls: raise Exception(f"mamanul ID not found: {mother_id}")
                if "father_candidates" in litter:
                    father_ids = litter["father_candidates"]
                else:
                    father_ids = [litter.get("father")]
                for father_id in father_ids:
                    if father_id and father_id not in self.manuls: raise Exception(f"papanul ID not found: {father_id}")
                kitten_ids = litter["kittens"]
                for kitten_id in kitten_ids:
                    if kitten_id and kitten_id not in self.manuls: raise Exception(f"minul ID not found: {kitten_id}")
                self.litters[litter_id] = litter

    def __del__(self):
        pass

    def getIndividuals(self, filter=""):
        return self.manuls

    def getIndividualByID(self, id):
        return self.manuls.get(id, None)

    def getZoos(self, filter=""):
        return self.zoos
